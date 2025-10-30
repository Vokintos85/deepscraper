"""Timing utilities."""

from __future__ import annotations

import random


def jitter(base: float, variance: float) -> float:
    return max(0.0, random.gauss(base, variance))


__all__ = ["jitter"]
