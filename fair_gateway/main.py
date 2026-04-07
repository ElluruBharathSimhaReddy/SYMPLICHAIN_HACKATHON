from __future__ import annotations

from .external_api import MockExternalAPI
from .fairness_queue import FairMultiTenantQueue, GatewayRequest, TokenBucketRateLimiter
from .worker import GatewayWorker


def build_demo_requests() -> list[GatewayRequest]:
    requests: list[GatewayRequest] = []

    # Customer A floods the system.
    for i in range(1, 11):
        requests.append(
            GatewayRequest(
                request_id=f"A-{i}",
                customer_id="Customer_A",
                payload={"document_id": i, "customer": "A"},
            )
        )

    # Customer B sends only one request.
    requests.append(
        GatewayRequest(
            request_id="B-1",
            customer_id="Customer_B",
            payload={"document_id": 1, "customer": "B"},
        )
    )

    # Customer C sends a small burst.
    for i in range(1, 4):
        requests.append(
            GatewayRequest(
                request_id=f"C-{i}",
                customer_id="Customer_C",
                payload={"document_id": i, "customer": "C"},
            )
        )
    return requests


def main() -> None:
    queue = FairMultiTenantQueue()
    queue.extend(build_demo_requests())

    api = MockExternalAPI(failure_rate=0.15)
    limiter = TokenBucketRateLimiter(rate_per_second=3, capacity=3)
    worker = GatewayWorker(queue=queue, api=api, limiter=limiter, max_retries=3)

    print("Starting fair dispatch demo...")
    print("Initial queue depths:", queue.customer_depths())
    worker.run()
    print("Completed:", len(worker.completed))
    print("Failed:", len(worker.failed))


if __name__ == "__main__":
    main()
