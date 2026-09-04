import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from models.schemas import Incident, Severity


ORDER_URL = "http://localhost:8080/order"

BASELINE_LATENCY_MS = 320.0
LATENCY_THRESHOLD_MULTIPLIER = 2.0


def measure_order_api(
    order_id: str,
    total: float = 100.0,
    product_id: str = "1",
    quantity: int = 1,
) -> dict:
    """Send an order and measure the Order API response time."""

    payload = (
        f'{{'
        f'"orderId":"{order_id}",'
        f'"total":{total},'
        f'"items":[{{'
        f'"productId":"{product_id}",'
        f'"quantity":{quantity}'
        f'}}]'
        f'}}'
    ).encode("utf-8")

    request = Request(
        ORDER_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    start_time = time.perf_counter()

    try:
        with urlopen(request, timeout=10) as response:
            response.read()
            status_code = response.status

    except HTTPError as error:
        status_code = error.code

    except URLError as error:
        return {
            "success": False,
            "status_code": None,
            "latency_ms": None,
            "incident_detected": False,
            "error": f"Could not connect to application: {error}",
        }

    except Exception as error:
        return {
            "success": False,
            "status_code": None,
            "latency_ms": None,
            "incident_detected": False,
            "error": str(error),
        }

    latency_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    increase_percent = round(
        ((latency_ms - BASELINE_LATENCY_MS)
         / BASELINE_LATENCY_MS) * 100,
        2,
    )

    incident_detected = (
        latency_ms
        > BASELINE_LATENCY_MS * LATENCY_THRESHOLD_MULTIPLIER
    )

    return {
        "success": 200 <= status_code < 300,
        "status_code": status_code,
        "latency_ms": latency_ms,
        "baseline_latency_ms": BASELINE_LATENCY_MS,
        "increase_percent": increase_percent,
        "incident_detected": incident_detected,
        "endpoint": ORDER_URL,
        "service": "order-api",
        "order_id": order_id,
    }


def create_incident(result: dict) -> Incident | None:
    """Convert a detected monitoring event into our Incident model."""

    if not result.get("incident_detected"):
        return None

    return Incident(
        incident_id="INC-001",
        service_name="order-api",
        service_version="v1.8",
        severity=Severity.HIGH,
        detected_at=datetime.now(timezone.utc),
        symptom="Order API latency increased significantly.",
        baseline_latency_ms=result["baseline_latency_ms"],
        current_latency_ms=result["latency_ms"],
        increase_percent=result["increase_percent"],
        environment="production",
    )


if __name__ == "__main__":
    result = measure_order_api("MONITOR-TEST-001")

    print("\nE-COMMERCE API MONITOR")
    print("=" * 50)
    print(f"Endpoint          : {result.get('endpoint', ORDER_URL)}")
    print(f"Service           : {result.get('service', 'order-api')}")
    print(f"Status            : {result.get('status_code')}")
    print(f"Baseline          : {result.get('baseline_latency_ms')} ms")
    print(f"Current Latency   : {result.get('latency_ms')} ms")
    print(f"Increase          : {result.get('increase_percent')}%")
    print(f"Incident Detected : {result.get('incident_detected')}")
    print(f"Successful        : {result.get('success')}")

    if result.get("error"):
        print(f"Error             : {result['error']}")

    incident = create_incident(result)

    if incident:
        print("\n🚨 INCIDENT CREATED")
        print("=" * 50)
        print(incident.model_dump_json(indent=2))
    else:
        print("\n✅ No incident detected.")