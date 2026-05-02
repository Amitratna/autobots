"""Agent base class for the AUTOBOTS framework."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentMessage:
    """Message passed between agents."""
    sender: str
    recipient: str
    subject: str
    body: Dict[str, Any]
    attachments: List[str] = field(default_factory=list)


class BaseAgent(ABC):
    """Abstract base for all AUTOBOTS agents."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.mailbox: List[AgentMessage] = []

    def receive(self, message: AgentMessage) -> None:
        """Receive a message and add to mailbox."""
        self.mailbox.append(message)

    def send(
        self,
        recipient: "BaseAgent",
        subject: str,
        body: Dict[str, Any],
        attachments: Optional[List[str]] = None,
    ) -> AgentMessage:
        """Send a message to another agent."""
        msg = AgentMessage(
            sender=self.name,
            recipient=recipient.name,
            subject=subject,
            body=body,
            attachments=attachments or [],
        )
        recipient.receive(msg)
        return msg

    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """Execute the agent's primary task. Returns results."""
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}>"