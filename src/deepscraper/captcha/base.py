"""Captcha solving interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class CaptchaSolver(ABC):
    """Abstract captcha solver."""

    @abstractmethod
    async def solve_image(self, image_base64: str, captcha_type: str = "image") -> str:
        """Solve an image captcha and return the text/token."""

    @abstractmethod
    async def solve_sitekey(self, site_key: str, url: str, captcha_type: str = "recaptcha_v2") -> str:
        """Solve a sitekey-based captcha and return the token."""


class NullCaptchaSolver(CaptchaSolver):
    """Fallback solver that raises helpful errors."""

    async def solve_image(self, image_base64: str, captcha_type: str = "image") -> str:
        raise RuntimeError("Captcha solving requested but no provider configured.")

    async def solve_sitekey(self, site_key: str, url: str, captcha_type: str = "recaptcha_v2") -> str:
        raise RuntimeError("Captcha solving requested but no provider configured.")


def get_solver(provider: str, api_key: Optional[str]) -> CaptchaSolver:
    if provider == "twocaptcha" and api_key:
        from .twocaptcha import TwoCaptchaSolver

        return TwoCaptchaSolver(api_key)
    if provider == "capsolver" and api_key:
        from .capsolver import CapSolver

        return CapSolver(api_key)
    return NullCaptchaSolver()


__all__ = ["CaptchaSolver", "NullCaptchaSolver", "get_solver"]
