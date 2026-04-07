from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from time import monotonic, sleep
from typing import Deque, Dict, Iterable, List, Optional


@dataclass
class GatewayRequest:
    request_id: str
    customer_id: str
    payload: dict
    attempts: int = 0
    available_at: float = field(default_factory=monotonic)


class TokenBucketRateLimiter:
    """Global token bucket for hard rate enforcement.

    Capacity and refill rate are both set to 3 tokens/sec so short bursts never
    exceed 3 requests within a single second window.
    """

    def __init__(self, rate_per_second: int, capacity: int) -> None:
        self.rate_per_second = rate_per_second
        self.capacity = capacity
        self.tokens = float(capacity)
        self.last_refill = monotonic()

    def _refill(self) -> None:
        now = monotonic()
        elapsed = now - self.last_refill
        self.last_refill = now
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate_per_second)

    def acquire(self) -> None:
        while True:
            self._refill()
            if self.tokens >= 1:
                self.tokens -= 1
                return
            sleep(0.02)


class FairMultiTenantQueue:
    """Round-robin scheduler across customer queues.

    Each active customer gets one turn before a customer gets a second turn.
    This keeps fairness strong even when one tenant floods the system.
    """

    def __init__(self) -> None:
        self.queues: Dict[str, Deque[GatewayRequest]] = defaultdict(deque)
        self.active_customers: Deque[str] = deque()
        self.in_active_set: set[str] = set()

    def push(self, request: GatewayRequest) -> None:
        customer_queue = self.queues[request.customer_id]
        customer_queue.append(request)
        if request.customer_id not in self.in_active_set:
            self.active_customers.append(request.customer_id)
            self.in_active_set.add(request.customer_id)

    def extend(self, requests: Iterable[GatewayRequest]) -> None:
        for request in requests:
            self.push(request)

    def pop_ready(self) -> Optional[GatewayRequest]:
        if not self.active_customers:
            return None

        rounds = len(self.active_customers)
        for _ in range(rounds):
            customer_id = self.active_customers.popleft()
            queue = self.queues[customer_id]

            if not queue:
                self.in_active_set.discard(customer_id)
                continue

            request = queue[0]
            if request.available_at > monotonic():
                self.active_customers.append(customer_id)
                continue

            queue.popleft()
            if queue:
                self.active_customers.append(customer_id)
            else:
                self.in_active_set.discard(customer_id)

            return request

        return None

    def pending_count(self) -> int:
        return sum(len(q) for q in self.queues.values())

    def customer_depths(self) -> Dict[str, int]:
        return {customer_id: len(queue) for customer_id, queue in self.queues.items() if queue}
