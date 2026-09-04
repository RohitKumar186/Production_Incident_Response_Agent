from tools.ecommerce_monitor import measure_order_api


def get_ecommerce_metrics(
    order_id: str = "METRICS-TEST-001",
) -> list[dict]:
    """
    Collect real-time metrics from the e-commerce Order API.

    The current integration uses API response latency as the
    primary real-world metric.
    """

    result = measure_order_api(order_id)

    if result.get("latency_ms") is None:
        return []

    return [
        {
            "service": result.get("service", "order-api"),
            "incident_id": order_id,
            "latency_ms": result["latency_ms"],
            "baseline_latency_ms": result.get(
                "baseline_latency_ms",
                320.0,
            ),
            "cpu_percent": None,
            "error_rate_percent": (
                0.0 if result.get("success") else 100.0
            ),
            "status_code": result.get("status_code"),
        }
    ]


if __name__ == "__main__":
    metrics = get_ecommerce_metrics()

    print("\nE-COMMERCE REAL METRICS")
    print("=" * 50)

    if not metrics:
        print("No metrics collected.")
    else:
        for metric in metrics:
            print(f"Service          : {metric['service']}")
            print(f"Latency          : {metric['latency_ms']} ms")
            print(
                f"Baseline         : "
                f"{metric['baseline_latency_ms']} ms"
            )
            print(f"Status Code      : {metric['status_code']}")
            print(
                f"Error Rate       : "
                f"{metric['error_rate_percent']}%"
            )
            