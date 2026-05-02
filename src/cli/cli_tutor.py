#!/usr/bin/env python3
"""AI Agent Academy — Interactive CLI Tutor.

A terminal-based learning tool that teaches AI and AI Agent concepts
with interactive lessons, quizzes, and progress tracking.

Usage:
    python cli_tutor.py          # Main menu
    python cli_tutor.py --lesson 3   # Jump to lesson 3
    python cli_tutor.py --quiz       # Take a random quiz
"""

import argparse
import json
import os
import random
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.data.lessons import LESSONS, LESSON_MAP, TOTAL_LESSONS

# ─── ANSI colors ──────────────────────────────────────────────────────

class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BGRED = "\033[101m"
    BGGREEN = "\033[102m"
    BGBLUE = "\033[104m"


# ─── Progress ─────────────────────────────────────────────────────────

PROGRESS_DIR = Path.home() / ".aiacademy"
PROGRESS_FILE = PROGRESS_DIR / "progress.json"


def _load_progress() -> dict:
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {}


def _save_progress(data: dict):
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
    PROGRESS_FILE.write_text(json.dumps(data, indent=2))


def _get_lesson_progress(lesson_id: int) -> dict:
    p = _load_progress()
    return p.get(str(lesson_id), {"completed": False, "quiz_score": 0, "quiz_attempts": 0})


def _mark_lesson_completed(lesson_id: int):
    p = _load_progress()
    lid = str(lesson_id)
    if lid not in p:
        p[lid] = {}
    p[lid]["completed"] = True
    _save_progress(p)


def _save_quiz_score(lesson_id: int, score: int, total: int):
    p = _load_progress()
    lid = str(lesson_id)
    if lid not in p:
        p[lid] = {"completed": False}
    p[lid]["quiz_score"] = score
    p[lid]["quiz_total"] = total
    p[lid]["quiz_attempts"] = p[lid].get("quiz_attempts", 0) + 1
    if score == total:
        p[lid]["completed"] = True
    _save_progress(p)


def _overall_progress() -> float:
    p = _load_progress()
    if TOTAL_LESSONS == 0:
        return 0
    completed = sum(1 for v in p.values() if v.get("completed"))
    return completed / TOTAL_LESSONS


# ─── Display helpers ──────────────────────────────────────────────────

def clear():
    os.system("clear" if os.name == "posix" else "cls")


def banner():
    bar = f"{C.BGBLUE}{C.WHITE}{C.BOLD}"
    print(f"\n{bar}╔══════════════════════════════════════════════════════╗")
    print(f"{bar}║         🤖  AI AGENT ACADEMY  🤖                  ║")
    print(f"{bar}║     Learn AI Agents through interactive lessons    ║")
    print(f"{bar}╚══════════════════════════════════════════════════════╝{C.RESET}")
    pct = _overall_progress() * 100
    bar_w = 30
    filled = int(bar_w * _overall_progress())
    prog = f"{'█' * filled}{'░' * (bar_w - filled)}"
    print(f"\n  {C.BOLD}Progress:{C.RESET} [{prog}] {pct:.0f}%\n")


def print_lesson_card(lesson: dict):
    prog = _get_lesson_progress(lesson["id"])
    status_icon = f"{C.GREEN}✅{C.RESET}" if prog.get("completed") else f"{C.DIM}⬜{C.RESET}"
    score = prog.get("quiz_score", 0)
    total = prog.get("quiz_total", 0)
    score_str = f"  Quiz: {score}/{total}" if total else ""
    print(f"  {status_icon}  {C.BOLD}Lesson {lesson['id']}: {lesson['title']}{C.RESET}")
    print(f"     {lesson['summary']}{score_str}")
    print()


def print_lesson(lesson: dict):
    clear()
    banner()
    prog = _get_lesson_progress(lesson["id"])
    status = f"{C.GREEN}✅ Completed{C.RESET}" if prog.get("completed") else f"{C.YELLOW}In progress{C.RESET}"
    print(f"{C.BOLD}{C.CYAN}Lesson {lesson['id']}: {lesson['title']}{C.RESET}")
    print(f"  Status: {status}\n")
    print(lesson["content"])
    print()


# ─── Quiz ─────────────────────────────────────────────────────────────

def run_quiz(lesson: dict):
    questions = lesson.get("quiz_questions", [])
    if not questions:
        print(f"{C.YELLOW}No quiz available for this lesson.{C.RESET}")
        input(f"\n{C.DIM}Press Enter to continue...{C.RESET}")
        return

    random.shuffle(questions)
    score = 0

    print(f"\n{C.BOLD}{C.MAGENTA}📝 Quiz: {lesson['title']}{C.RESET}\n")
    print(f"{C.DIM}Answer {len(questions)} questions. Type the number of your answer.{C.RESET}\n")

    for i, q in enumerate(questions, 1):
        print(f"{C.BOLD}Q{i}: {q['question']}{C.RESET}")
        for j, opt in enumerate(q["options"]):
            print(f"  {j + 1}. {opt}")
        print()

        while True:
            try:
                ans = input(f"  {C.BOLD}Your answer (1-{len(q['options'])}): {C.RESET}").strip()
                ans_idx = int(ans) - 1
                if 0 <= ans_idx < len(q["options"]):
                    break
                print(f"  {C.RED}Enter a number between 1 and {len(q['options'])}{C.RESET}")
            except ValueError:
                print(f"  {C.RED}Please enter a number.{C.RESET}")

        if ans_idx == q["correct"]:
            print(f"  {C.GREEN}✅ Correct!{C.RESET}\n")
            score += 1
        else:
            correct_ans = q["options"][q["correct"]]
            print(f"  {C.RED}❌ Incorrect. The answer was: {correct_ans}{C.RESET}\n")

    # Results
    pct = int(score / len(questions) * 100)
    if pct >= 80:
        grade = f"{C.GREEN}{C.BOLD}PASSED{C.RESET}"
    else:
        grade = f"{C.YELLOW}Review needed{C.RESET}"

    print(f"{'='*50}")
    print(f"  {C.BOLD}Score: {score}/{len(questions)} ({pct}%) — {grade}{C.RESET}")

    _save_quiz_score(lesson["id"], score, len(questions))

    input(f"\n{C.DIM}Press Enter to return to lesson...{C.RESET}")


# ─── Main menu ───────────────────────────────────────────────────────

def main_menu():
    while True:
        clear()
        banner()
        print(f"  {C.BOLD}{C.YELLOW}Available Lessons:{C.RESET}\n")
        for lesson in LESSONS:
            print_lesson_card(lesson)
        print(f"  {C.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.RESET}")
        print(f"  {C.BOLD}q{C.RESET})  Quit")
        print()

        choice = input(f"  {C.BOLD}Select a lesson (1-{TOTAL_LESSONS}): {C.RESET}").strip()
        if choice.lower() == "q":
            clear()
            print(f"\n  {C.CYAN}Keep learning! 🚀{C.RESET}\n")
            sys.exit(0)

        try:
            lid = int(choice)
            if 1 <= lid <= TOTAL_LESSONS:
                lesson_view(lid)
            else:
                print(f"  {C.RED}Enter a number between 1 and {TOTAL_LESSONS}{C.RESET}")
                input(f"{C.DIM}Press Enter...{C.RESET}")
        except ValueError:
            print(f"  {C.RED}Invalid choice.{C.RESET}")
            input(f"{C.DIM}Press Enter...{C.RESET}")


def lesson_view(lesson_id: int):
    lesson = LESSON_MAP.get(lesson_id)
    if not lesson:
        return

    while True:
        print_lesson(lesson)
        print(f"  {C.BOLD}Options:{C.RESET}")
        print(f"  1)  Take quiz ({len(lesson['quiz_questions'])} questions)")
        print(f"  2)  Mark as completed")
        print(f"  3)  View my progress")
        print(f"  b)  Back to menu")
        print()

        choice = input(f"  {C.BOLD}Choose: {C.RESET}").strip()

        if choice == "1":
            run_quiz(lesson)
        elif choice == "2":
            _mark_lesson_completed(lesson_id)
            print(f"  {C.GREEN}✅ Lesson marked as completed!{C.RESET}")
            input(f"{C.DIM}Press Enter...{C.RESET}")
        elif choice == "3":
            prog = _get_lesson_progress(lesson_id)
            print(f"\n  {C.BOLD}Progress for Lesson {lesson_id}:{C.RESET}")
            print(f"    Completed: {'Yes' if prog.get('completed') else 'No'}")
            print(f"    Quiz score: {prog.get('quiz_score', '-')}/{prog.get('quiz_total', '-')}")
            print(f"    Attempts: {prog.get('quiz_attempts', 0)}")
            input(f"\n{C.DIM}Press Enter...{C.RESET}")
        elif choice.lower() == "b":
            break


# ─── CLI entry ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AI Agent Academy — CLI Tutor")
    parser.add_argument("--lesson", type=int, help="Jump directly to a lesson")
    parser.add_argument("--quiz", action="store_true", help="Take a random quiz")
    args = parser.parse_args()

    try:
        if args.lesson:
            if 1 <= args.lesson <= TOTAL_LESSONS:
                lesson_view(args.lesson)
            else:
                print(f"Lesson {args.lesson} not found. Choose 1-{TOTAL_LESSONS}")
        elif args.quiz:
            lesson = random.choice(LESSONS)
            print(f"Random quiz: {lesson['title']}")
            run_quiz(lesson)
        else:
            main_menu()
    except KeyboardInterrupt:
        print(f"\n\n  {C.CYAN}See you next time! 🚀{C.RESET}\n")


if __name__ == "__main__":
    main()