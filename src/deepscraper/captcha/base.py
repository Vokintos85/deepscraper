# src/deepscraper/captcha/base.py
"""Base interface for captcha solving services."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class CaptchaSolver(ABC):
    """Abstract base class for captcha solving services."""

    @abstractmethod
    async def solve_recaptcha_v2(
        self,
        site_key: str,
        url: str,
        invisible: bool = False
    ) -> str:
        """Solve reCAPTCHA v2."""
        pass

    @abstractmethod
    async def solve_recaptcha_v3(
        self,
        site_key: str,
        url: str,
        action: str = "verify",
        min_score: float = 0.5
    ) -> str:
        """Solve reCAPTCHA v3."""
        pass

    @abstractmethod
    async def solve_image_captcha(
        self,
        image_url: str,
        **kwargs: Any
    ) -> str:
        """Solve image-based captcha from URL."""
        pass

    @abstractmethod
    async def solve_image_captcha_base64(
        self,
        image_base64: str,
        **kwargs: Any
    ) -> str:
        """Solve image-based captcha from base64 string."""
        pass

    @abstractmethod
    async def solve_hcaptcha(
        self,
        site_key: str,
        url: str
    ) -> str:
        """Solve hCaptcha."""
        pass

    @abstractmethod
    async def get_balance(self) -> float:
        """Get account balance."""
        pass


class NullCaptchaSolver(CaptchaSolver):
    """Fallback solver that raises helpful errors."""

    async def solve_recaptcha_v2(self, site_key: str, url: str, invisible: bool = False) -> str:
        raise RuntimeError("Captcha solving requested but no provider configured.")

    async def solve_recaptcha_v3(self, site_key: str, url: str, action: str = "verify", min_score: float = 0.5) -> str:
        raise RuntimeError("Captcha solving requested but no provider configured.")

    async def solve_image_captcha(self, image_url: str, **kwargs: Any) -> str:
        raise RuntimeError("Captcha solving requested but no provider configured.")

    async def solve_image_captcha_base64(self, image_base64: str, **kwargs: Any) -> str:
        raise RuntimeError("Captcha solving requested but no provider configured.")

    async def solve_hcaptcha(self, site_key: str, url: str) -> str:
        raise RuntimeError("Captcha solving requested but no provider configured.")

    async def get_balance(self) -> float:
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