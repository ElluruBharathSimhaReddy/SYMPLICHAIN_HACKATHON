from __future__ import annotations

import random
from time import monotonic, sleep
from typing import List

from .external_api import MockExternalAPI
from .fairness_queue import FairMultiTenantQueue, GatewayRequest, TokenBucketRateLimiter


class GatewayWorker:
    def __init__(
        self,
        queue: FairMultiTenantQueue,
        api: MockExternalAPI,
        limiter: TokenBucketRateLimiter,
        max_retries: int = 3,
    ) -> None:
        self.queue = queue
        self.api = api
        self.limiter = limiter
        self.max_retries = max_retries
        self.completed: List[str] = []
        self.failed: List[str] = []

    def _schedule_retry(self, request: GatewayRequest) -> None:
        request.attempts += 1
        if request.attempts > self.max_retries:
            self.failed.append(request.request_id)
            print(f"FAILED permanently: {request.request_id} for {request.customer_id}")
            return

        backoff_seconds = min(2 ** request.attempts, 8)
        jitter = random.uniform(0.0, 0.4)
        request.available_at = monotonic() + backoff_seconds + jitter
        self.queue.push(request)
        print(
            f"RETRY scheduled: {request.request_id} for {request.customer_id} "
            f"in {backoff_seconds + jitter:.2f}s"
        )

    def run(self) -> None:
        while self.queue.pending_count() > 0:
            request = self.queue.pop_ready()
            if request is None:
                sleep(0.05)
                continue

            self.limiter.acquire()
            response = self.api.send(request.payload)
            if response.ok:
                self.completed.append(request.request_id)
                print(
                    f"SUCCESS customer={request.customer_id:<12} "
                    f"request={request.request_id:<8} attempts={request.attempts}"
                )
            else:
                print(
                    f"ERROR   customer={request.customer_id:<12} "
                    f"request={request.request_id:<8} status={response.status_code}"
                )
                self._schedule_retry(request)
