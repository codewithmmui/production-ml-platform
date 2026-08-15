import argparse
import concurrent.futures
import json
import time
import urllib.request

PAYLOAD = json.dumps(
    {
        "customer_id": "LOAD-1",
        "tenure_months": 13,
        "monthly_spend": 79.99,
        "total_spend": 1020.5,
        "support_tickets": 4,
        "login_frequency": 3,
        "subscription_plan": "premium",
        "payment_failures": 2,
        "days_since_last_login": 15,
        "usage_score": 0.42,
        "contract_type": "monthly",
        "region": "south",
    }
).encode()


def hit(url: str) -> tuple[float, bool]:
    start = time.perf_counter()
    try:
        request = urllib.request.Request(url, PAYLOAD, {"content-type": "application/json"})
        with urllib.request.urlopen(request, timeout=5) as response:
            ok = response.status == 200
    except Exception:
        ok = False
    return (time.perf_counter() - start) * 1000, ok


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000/predict")
    parser.add_argument("--requests", type=int, default=1000)
    parser.add_argument("--concurrency", type=int, default=20)
    args = parser.parse_args()
    started = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(args.concurrency) as pool:
        results = list(pool.map(lambda _: hit(args.url), range(args.requests)))
    elapsed = time.perf_counter() - started
    latencies = sorted(value for value, _ in results)

    def percentile(p: float) -> float:
        return latencies[min(int(len(latencies) * p), len(latencies) - 1)]

    print(
        json.dumps(
            {
                "requests_per_second": args.requests / elapsed,
                "p50_ms": percentile(0.50),
                "p95_ms": percentile(0.95),
                "p99_ms": percentile(0.99),
                "error_rate": sum(not ok for _, ok in results) / args.requests,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
