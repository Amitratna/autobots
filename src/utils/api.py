"""APIs — wrappers for external service calls.

Phase 4 replaces stubs with real Etsy, Gumroad, and NVIDIA API clients.
"""

from typing import Any, Dict


class EtsyAPI:
    """Stub for Etsy API integration."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    def create_listing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new product listing."""
        # Stub — replace with requests.post to Etsy Open API v3
        return {
            "platform": "etsy",
            "status": "stub",
            "listing_id": "etsy_stub_001",
            "url": f"https://www.etsy.com/listing/stub_001",
        }


class GumroadAPI:
    """Stub for Gumroad API integration."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    def create_product(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Gumroad product."""
        # Stub — replace with requests.post to Gumroad API
        return {
            "platform": "gumroad",
            "status": "stub",
            "product_id": "gumroad_stub_001",
            "url": "https://gumroad.com/l/stub_001",
        }


class NvidiaAPIClient:
    """Client for NVIDIA AI image generation."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.base_url = "https://api.nvidia.com/v1"

    def generate_image(self, prompt: str) -> str:
        """Generate an image from a text prompt."""
        # Stub — replace with actual API call
        return f"nvidia_generated_{hash(prompt) % 10000:04d}.png"