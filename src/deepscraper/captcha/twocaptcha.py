"""2Captcha adapter."""

from __future__ import annotations

import asyncio
from typing import Any, Dict

import httpx

from .base import CaptchaSolver


class TwoCaptchaSolver(CaptchaSolver):
    API_URL = "https://2captcha.com"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._client = httpx.AsyncClient(base_url=self.API_URL, timeout=30.0)

    async def _poll_result(self, request_id: str) -> str:
        await asyncio.sleep(5)
        for _ in range(24):
            response = await self._client.get(
                "/res.php", params={"key": self._api_key, "action": "get", "id": request_id, "json": 1}
            )
            data = response.json()
            if data.get("status") == 1:
                return data["request"]
            await asyncio.sleep(5)
        raise RuntimeError("Captcha solving timeout")

    async def solve_image(self, image_base64: str, captcha_type: str = "image") -> str:
        response = await self._client.post(
            "/in.php",
            data={
                "key": self._api_key,
                "method": "base64",
                "body": image_base64,
                "json": 1,
            },
        )
        data = response.json()
        if data.get("status") != 1:
            raise RuntimeError(f"2Captcha error: {data}")
        return await self._poll_result(data["request"])

    async def solve_sitekey(self, site_key: str, url: str, captcha_type: str = "recaptcha_v2") -> str:
        response = await self._client.post(
            "/in.php",
            data={
                "key": self._api_key,
                "method": captcha_type,
                "googlekey": site_key,
                "pageurl": url,
                "json": 1,
            },
        )
        data = response.json()
        if data.get("status") != 1:
            raise RuntimeError(f"2Captcha error: {data}")
        return await self._poll_result(data["request"])

    async def close(self) -> None:
        await self._client.aclose()


__all__ = ["TwoCaptchaSolver"]
