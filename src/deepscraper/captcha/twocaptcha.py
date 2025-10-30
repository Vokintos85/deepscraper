# src/deepscraper/captcha/twocaptcha.py
"""2Captcha.com service implementation."""
from __future__ import annotations

import base64
import time
from typing import Optional, Dict, Any
import httpx

from .base import CaptchaSolver


class TwoCaptchaSolver(CaptchaSolver):
    """2Captcha.com captcha solving service."""

    BASE_URL = "https://2captcha.com"

    def __init__(self, api_key: str, timeout: int = 120, polling_interval: int = 5):
        self.api_key = api_key
        self.timeout = timeout
        self.polling_interval = polling_interval
        self._client = httpx.AsyncClient(timeout=timeout)

    async def solve_recaptcha_v2(
        self,
        site_key: str,
        url: str,
        invisible: bool = False
    ) -> str:
        """Solve reCAPTCHA v2."""
        method = "userrecaptcha"

        params = {
            "key": self.api_key,
            "method": method,
            "googlekey": site_key,
            "pageurl": url,
            "json": 1
        }

        if invisible:
            params["invisible"] = 1

        # Send captcha to service
        response = await self._client.post(f"{self.BASE_URL}/in.php", data=params)
        result = response.json()

        if result["status"] != 1:
            raise Exception(f"2Captcha error: {result.get('request', 'Unknown error')}")

        captcha_id = result["request"]

        # Wait for solution
        return await self._wait_for_solution(captcha_id)

    async def solve_recaptcha_v3(
        self,
        site_key: str,
        url: str,
        action: str = "verify",
        min_score: float = 0.5
    ) -> str:
        """Solve reCAPTCHA v3."""
        params = {
            "key": self.api_key,
            "method": "userrecaptcha",
            "version": "v3",
            "googlekey": site_key,
            "pageurl": url,
            "action": action,
            "min_score": min_score,
            "json": 1
        }

        response = await self._client.post(f"{self.BASE_URL}/in.php", data=params)
        result = response.json()

        if result["status"] != 1:
            raise Exception(f"2Captcha error: {result.get('request', 'Unknown error')}")

        captcha_id = result["request"]
        return await self._wait_for_solution(captcha_id)

    async def solve_image_captcha(
        self,
        image_url: str,
        **kwargs: Any
    ) -> str:
        """Solve image-based captcha from URL."""
        # Download image
        response = await self._client.get(image_url)
        image_data = response.content

        return await self.solve_image_captcha_base64(
            base64.b64encode(image_data).decode('utf-8'),
            **kwargs
        )

    async def solve_image_captcha_base64(
        self,
        image_base64: str,
        **kwargs: Any
    ) -> str:
        """Solve image-based captcha from base64 string."""
        params = {
            "key": self.api_key,
            "method": "base64",
            "body": image_base64,
            "json": 1
        }

        # Add additional parameters
        if "numeric" in kwargs:
            params["numeric"] = kwargs["numeric"]
        if "min_len" in kwargs:
            params["min_len"] = kwargs["min_len"]
        if "max_len" in kwargs:
            params["max_len"] = kwargs["max_len"]
        if "phrase" in kwargs:
            params["phrase"] = kwargs["phrase"]
        if "regsense" in kwargs:
            params["regsense"] = kwargs["regsense"]
        if "calc" in kwargs:
            params["calc"] = kwargs["calc"]

        response = await self._client.post(f"{self.BASE_URL}/in.php", data=params)
        result = response.json()

        if result["status"] != 1:
            raise Exception(f"2Captcha error: {result.get('request', 'Unknown error')}")

        captcha_id = result["request"]
        return await self._wait_for_solution(captcha_id)

    async def solve_hcaptcha(
        self,
        site_key: str,
        url: str
    ) -> str:
        """Solve hCaptcha."""
        params = {
            "key": self.api_key,
            "method": "hcaptcha",
            "sitekey": site_key,
            "pageurl": url,
            "json": 1
        }

        response = await self._client.post(f"{self.BASE_URL}/in.php", data=params)
        result = response.json()

        if result["status"] != 1:
            raise Exception(f"2Captcha error: {result.get('request', 'Unknown error')}")

        captcha_id = result["request"]
        return await self._wait_for_solution(captcha_id)

    async def _wait_for_solution(self, captcha_id: str) -> str:
        """Wait for captcha solution."""
        start_time = time.time()

        while time.time() - start_time < self.timeout:
            # Check solution status
            response = await self._client.get(
                f"{self.BASE_URL}/res.php",
                params={
                    "key": self.api_key,
                    "action": "get",
                    "id": captcha_id,
                    "json": 1
                }
            )

            result = response.json()

            if result["status"] == 1:
                return result["request"]  # Solution
            elif result["request"] != "CAPCHA_NOT_READY":
                raise Exception(f"2Captcha error: {result['request']}")

            # Wait before next check
            await asyncio.sleep(self.polling_interval)

        raise Exception("2Captcha timeout: Solution not received in time")

    async def get_balance(self) -> float:
        """Get account balance."""
        response = await self._client.get(
            f"{self.BASE_URL}/res.php",
            params={
                "key": self.api_key,
                "action": "getbalance",
                "json": 1
            }
        )

        result = response.json()
        if result["status"] == 1:
            return float(result["request"])
        else:
            raise Exception(f"2Captcha balance error: {result.get('request', 'Unknown error')}")

    async def aclose(self) -> None:
        """Close HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()


__all__ = ["TwoCaptchaSolver"]