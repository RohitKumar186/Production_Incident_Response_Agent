from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

LOG_FILE = (
    PROJECT_ROOT
    / "ecommerce-application"
    / "application"
    / "logs"
    / "ecommerce-application.log"
)


def search_ecommerce_logs(
    service: str = "order-api",
    order_id: str | None = None,
) -> list[dict]:
    """
    Search the real e-commerce application's log file.

    The e-commerce application does not know our internal incident ID,
    so filtering is based on the service endpoint and, when available,
    the order ID.
    """

    if not LOG_FILE.exists():
        return []

    results = []

    try:
        lines = LOG_FILE.read_text(
            encoding="utf-8",
            errors="replace",
        ).splitlines()
    except OSError:
        return []

    for line in lines:
        line_lower = line.lower()

        if service == "order-api":
            if (
                'post "/order"' not in line_lower
                and "ordercontroller" not in line_lower
            ):
                continue

        if order_id and order_id not in line:
            continue

        results.append(
            {
                "source": "ecommerce_application",
                "service": service,
                "reference": "ecommerce-application.log",
                "message": line.strip(),
            }
        )

    return results


if __name__ == "__main__":
    logs = search_ecommerce_logs()

    print("\nE-COMMERCE REAL LOG TOOL")
    print("=" * 60)
    print(f"Log file : {LOG_FILE}")
    print(f"Entries  : {len(logs)}")

    for entry in logs[-10:]:
        print(entry["message"])