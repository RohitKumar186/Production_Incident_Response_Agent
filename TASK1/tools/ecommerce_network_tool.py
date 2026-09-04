import time
from urllib.request import Request, urlopen
from urllib.error import URLError


ECOMMERCE_URL = "http://localhost:8080/incident/database"


def get_ecommerce_network_metrics() -> dict:
    """Measure network connectivity to the real e-commerce application."""

    request = Request(
        ECOMMERCE_URL,
        method="GET",
    )

    start_time = time.perf_counter()

    try:
        with urlopen(request, timeout=5) as response:
            response.read()
            status_code = response.status

    except URLError as error:
        return {
            "status": "UNAVAILABLE",
            "latency_ms": None,
            "packet_loss_percent": 100.0,
            "status_code": None,
            "error": str(error),
        }

    except Exception as error:
        return {
            "status": "UNAVAILABLE",
            "latency_ms": None,
            "packet_loss_percent": 100.0,
            "status_code": None,
            "error": str(error),
        }

    latency_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    return {
        "status": "HEALTHY" if 200 <= status_code < 500 else "DEGRADED",
        "latency_ms": latency_ms,
        "packet_loss_percent": 0.0,
        "status_code": status_code,
        "endpoint": ECOMMERCE_URL,
    }


if __name__ == "__main__":
    result = get_ecommerce_network_metrics()

    print("\nE-COMMERCE NETWORK METRICS")
    print("=" * 50)
    print(f"Endpoint       : {ECOMMERCE_URL}")
    print(f"Status         : {result['status']}")
    print(f"Latency        : {result['latency_ms']} ms")
    print(f"Packet Loss    : {result['packet_loss_percent']}%")
    print(f"HTTP Status    : {result['status_code']}")

    if result.get("error"):
        print(f"Error          : {result['error']}")