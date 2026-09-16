"""
Simulated production environment.

Generates realistic normal and incident states
for different controlled failure scenarios.
"""

from random import Random


SUPPORTED_SCENARIOS = {
    "database",
    "network",
    "application",
    "infrastructure",
}


def generate_environment(
    seed: int | None = None,
    scenario: str = "database",
) -> dict:
    """
    Generate a simulated production environment.

    Supported scenarios:
        - database
        - network
        - application
        - infrastructure

    A seed can be provided to make the simulation
    reproducible during testing.
    """

    scenario = scenario.lower()

    if scenario not in SUPPORTED_SCENARIOS:
        raise ValueError(
            f"Unsupported scenario: {scenario}. "
            f"Supported scenarios: {sorted(SUPPORTED_SCENARIOS)}"
        )

    rng = Random(seed)

    # -------------------------------------------------
    # Normal production state
    # -------------------------------------------------

    normal = {
        "service": "order-api",
        "version": "v1.8",
        "environment": "production",
        "latency_ms": rng.randint(95, 105),
        "cpu_percent": rng.randint(40, 50),
        "error_rate_percent": round(
            rng.uniform(0.1, 0.4),
            2,
        ),
        "database_query_latency_ms": rng.randint(
            250,
            350,
        ),
        "network_latency_ms": rng.randint(
            18,
            25,
        ),
        "packet_loss_percent": 0,
    }

    # -------------------------------------------------
    # Start with a healthy incident state
    # -------------------------------------------------

    incident = {
        "service": "order-api",
        "version": "v1.8",
        "environment": "production",

        # Service metrics
        "latency_ms": rng.randint(110, 130),
        "cpu_percent": rng.randint(45, 55),
        "error_rate_percent": round(
            rng.uniform(0.2, 0.5),
            2,
        ),

        # Database
        "database_query_latency_ms": rng.randint(
            300,
            400,
        ),

        # Network
        "network_latency_ms": rng.randint(
            20,
            25,
        ),
        "packet_loss_percent": 0,
    }

    # -------------------------------------------------
    # DATABASE FAILURE
    # -------------------------------------------------

    if scenario == "database":

        incident["latency_ms"] = rng.randint(
            480,
            520,
        )

        incident["cpu_percent"] = rng.randint(
            80,
            90,
        )

        incident["error_rate_percent"] = round(
            rng.uniform(7.5, 9.5),
            2,
        )

        incident["database_query_latency_ms"] = rng.randint(
            3900,
            4500,
        )

        # Network remains healthy
        incident["network_latency_ms"] = rng.randint(
            20,
            25,
        )

        incident["packet_loss_percent"] = 0

    # -------------------------------------------------
    # NETWORK FAILURE
    # -------------------------------------------------

    elif scenario == "network":

        incident["latency_ms"] = rng.randint(
            450,
            550,
        )

        incident["cpu_percent"] = rng.randint(
            45,
            60,
        )

        incident["error_rate_percent"] = round(
            rng.uniform(5.0, 8.0),
            2,
        )

        # Database remains relatively healthy
        incident["database_query_latency_ms"] = rng.randint(
            300,
            450,
        )

        # Network becomes unhealthy
        incident["network_latency_ms"] = rng.randint(
            400,
            700,
        )

        incident["packet_loss_percent"] = round(
            rng.uniform(10.0, 25.0),
            2,
        )

    # -------------------------------------------------
    # APPLICATION FAILURE
    # -------------------------------------------------

    elif scenario == "application":

        incident["latency_ms"] = rng.randint(
            400,
            600,
        )

        incident["cpu_percent"] = rng.randint(
            75,
            95,
        )

        incident["error_rate_percent"] = round(
            rng.uniform(15.0, 25.0),
            2,
        )

        # Database remains healthy
        incident["database_query_latency_ms"] = rng.randint(
            280,
            400,
        )

        # Network remains healthy
        incident["network_latency_ms"] = rng.randint(
            20,
            30,
        )

        incident["packet_loss_percent"] = 0

    # -------------------------------------------------
    # INFRASTRUCTURE FAILURE
    # -------------------------------------------------

    elif scenario == "infrastructure":

        incident["latency_ms"] = rng.randint(
            500,
            700,
        )

        incident["cpu_percent"] = rng.randint(
            90,
            99,
        )

        incident["error_rate_percent"] = round(
            rng.uniform(10.0, 18.0),
            2,
        )

        # Database remains healthy
        incident["database_query_latency_ms"] = rng.randint(
            280,
            400,
        )

        # Network remains healthy
        incident["network_latency_ms"] = rng.randint(
            20,
            30,
        )

        incident["packet_loss_percent"] = 0

    return {
        "scenario": scenario,
        "normal": normal,
        "incident": incident,
    }


if __name__ == "__main__":
    for scenario in sorted(SUPPORTED_SCENARIOS):

        environment = generate_environment(
            seed=42,
            scenario=scenario,
        )

        print("\n" + "=" * 60)
        print(f"SCENARIO: {scenario.upper()}")
        print("=" * 60)

        print("\nNormal State:")
        print(environment["normal"])

        print("\nIncident State:")
        print(environment["incident"])