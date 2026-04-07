from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class ExternalAPIResponse:
    ok: bool
    status_code: int
    message: str


class MockExternalAPI:
    """Fake shared API with occasional 5xx failures."""

    def __init__(self, failure_rate: float = 0.18) -> None:
        self.failure_rate = failure_rate

    def send(self, payload: dict) -> ExternalAPIResponse:
        if random.random() < self.failure_rate:
            return ExternalAPIResponse(False, 503, "temporary upstream failure")
        return ExternalAPIResponse(True, 200, f"processed {payload}")
