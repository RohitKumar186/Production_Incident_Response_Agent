"""
Simulated production environment.

Generates realistic normal and incident states automatically.
"""

from random import Random


def generate_environment(seed: int | None = None) -> dict:
    """
    Generate a simulated production environment.

    A seed can be provided to make the simulation reproducible
    during testing.
    """

    rng = Random(seed)

    # -------------------------
    # Normal production state
    # -------------------------

    normal = {
        "service": "order-api",
        "version": "v1.8",
        "environment": "production",
        "latency_ms": rng.randint(95, 105),
        "cpu_percent": rng.randint(40, 50),
        "error_rate_percent": round(rng.uniform(0.1, 0.4), 2),
        "database_query_latency_ms": rng.randint(250, 350),
        "network_latency_ms": rng.randint(18, 25),
    }

    # -------------------------
    # Incident production state
    # -------------------------

    incident = {
        "service": "order-api",
        "version": "v1.8",
        "environment": "production",
        "latency_ms": rng.randint(480, 520),
        "cpu_percent": rng.randint(80, 90),
        "error_rate_percent": round(rng.uniform(7.5, 9.5), 2),
        "database_query_latency_ms": rng.randint(3900, 4500),
        "network_latency_ms": rng.randint(20, 25),
    }

    return {
        "normal": normal,
        "incident": incident,
    }


if __name__ == "__main__":
    environment = generate_environment()

    print("Environment Generated")
    print("---------------------")

    print("\nNormal State:")
    print(environment["normal"])

    print("\nIncident State:")
    print(environment["incident"])