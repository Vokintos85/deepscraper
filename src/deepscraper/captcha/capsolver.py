"""CapSolver adapter stub."""

from __future__ import annotations

import asyncio
import httpx

from .base import CaptchaSolver


class CapSolver(CaptchaSolver):
    API_URL = "https://api.capsolver.com"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._client = httpx.AsyncClient(base_url=self.API_URL, timeout=30.0)

    async def _solve(self, payload: dict) -> str:
        response = await self._client.post("/createTask", json={"clientKey": self._api_key, **payload})
        data = response.json()
        task_id = data.get("taskId")
        if not task_id:
            raise RuntimeError(f"CapSolver error: {data}")
        for _ in range(24):
            await asyncio.sleep(5)
            result = await self._client.post("/getTaskResult", json={"clientKey": self._api_key, "taskId": task_id})
            body = result.json()
            if body.get("status") == "ready":
                return body["solution"].get("gRecaptchaResponse", "") or body["solution"].get("text", "")
        raise RuntimeError("CapSolver timeout")

    async def solve_image(self, image_base64: str, captcha_type: str = "image") -> str:
        payload = {
            "task": {
                "type": "ImageToTextTask",
                "body": image_base64,
            }
        }
        return await self._solve(payload)

    async def solve_sitekey(self, site_key: str, url: str, captcha_type: str = "RecaptchaV2TaskProxyless") -> str:
        payload = {
            "task": {
                "type": captcha_type,
                "websiteURL": url,
                "websiteKey": site_key,
            }
        }
        return await self._solve(payload)

    async def close(self) -> None:
        await self._client.aclose()


__all__ = ["CapSolver"]
