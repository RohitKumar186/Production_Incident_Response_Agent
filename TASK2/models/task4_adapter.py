from dataclasses import dataclass
from typing import Any


@dataclass
class Task4Incident:
    """
    Compatibility representation of an incident for Task 4.

    This adapter translates the new Task 1/2 incident model into
    the legacy structure currently expected by Task 4.

    This is NOT the simulator's hidden root cause.
    """

    incident_id: str
    service: dict[str, Any]
    symptom: dict[str, Any]
    incident_type: str
    technology_stack: list[str]


@dataclass
class Task4Finding:
    """
    Compatibility representation of one investigation finding.

    This matches the fields currently consumed by Task 4 RCA.
    """

    finding_id: str
    agent: str
    finding: str
    category: str
    value: Any
    evidence: str
    expected_value: str | None
    confidence: float


@dataclass
class Task4Payload:
    """
    Compatibility payload expected by the current Task 4
    investigation orchestrator.
    """

    incident: Task4Incident
    findings: list[Task4Finding]


@dataclass
class Task4InvestigationInput:
    """
    Compatibility wrapper expected by Task 4.

    The adapter allows our redesigned Task 2 to communicate with
    the existing Task 4 interface without changing Task 4 itself.
    """

    incident_id: str
    payload: Task4Payload


class Task4Adapter:
    """
    Converts the redesigned Task 2 InvestigationCard into the
    structure expected by the current Task 4 implementation.

    Important:
        - No simulator root cause is copied.
        - No SimulatedFault is copied.
        - Only observed investigation evidence is transferred.
    """

    def convert(self, investigation_card) -> Task4InvestigationInput:
        """
        Convert a Task 2 InvestigationCard into Task 4's
        expected input structure.
        """

        incident = Task4Incident(
            incident_id=investigation_card.incident_id,
            service={
                "name": investigation_card.affected_component,
                "version": "simulated",
            },
            symptom={
                "description": (
                    "; ".join(
                        investigation_card.observed_symptoms
                    )
                )
            },
            incident_type=investigation_card.incident_type,
            technology_stack=(
                investigation_card.technology_stack
            ),
        )

        findings = []

        for index, evidence_item in enumerate(
            investigation_card.evidence,
            start=1,
        ):

            source = evidence_item.get(
                "source",
                "unknown",
            )

            component = evidence_item.get(
                "component",
                investigation_card.affected_component,
            )

            data = evidence_item.get(
                "data",
                {},
            )

            finding_text = self._build_finding_text(
                source=source,
                component=component,
                data=data,
            )

            category = self._map_category(
                source=source,
                component=component,
            )

            value = self._extract_primary_value(
                data
            )

            expected_value = self._expected_value(
                category=category,
                data=data,
            )

            findings.append(
                Task4Finding(
                    finding_id=(
                        f"{investigation_card.incident_id}"
                        f"-F{index:03d}"
                    ),
                    agent="TASK2",
                    finding=finding_text,
                    category=category,
                    value=value,
                    evidence=str(data),
                    expected_value=expected_value,
                    confidence=self._calculate_confidence(
                        data
                    ),
                )
            )

        payload = Task4Payload(
            incident=incident,
            findings=findings,
        )

        return Task4InvestigationInput(
            incident_id=investigation_card.incident_id,
            payload=payload,
        )

    # ============================================================
    # FINDING TEXT
    # ============================================================

    def _build_finding_text(
        self,
        source: str,
        component: str,
        data: Any,
    ) -> str:
        """
        Convert raw Task 3 evidence into a concise finding.

        This does not attempt to determine root cause.
        """

        if isinstance(data, list):

            if not data:
                return (
                    f"No log events were returned for "
                    f"{component}."
                )

            messages = []

            for entry in data:

                if isinstance(entry, dict):

                    message = entry.get(
                        "message"
                    )

                    if message:
                        messages.append(
                            str(message)
                        )

            if messages:

                return (
                    f"Logs for {component}: "
                    + " | ".join(messages)
                )

            return (
                f"Log evidence collected for "
                f"{component}."
            )

        if isinstance(data, dict):

            observations = []

            for key, value in data.items():

                if value is None:
                    continue

                observations.append(
                    f"{key}={value}"
                )

            if observations:

                return (
                    f"{source} evidence for {component}: "
                    + ", ".join(observations)
                )

        return (
            f"{source} evidence collected for "
            f"{component}."
        )

    # ============================================================
    # CATEGORY
    # ============================================================

    def _map_category(
        self,
        source: str,
        component: str,
    ) -> str:
        """
        Map Task 3 evidence sources into categories understood
        by the current Task 4 RCA implementation.
        """

        source_lower = source.lower()

        if "database" in source_lower:
            return "DATABASE"

        if "network" in source_lower:
            return "NETWORK"

        if "infrastructure" in source_lower:
            return "INFRASTRUCTURE"

        if "dependency" in source_lower:
            return "APPLICATION"

        if source_lower == "logs":
            return "LOGS"

        if source_lower == "metrics":
            return "METRICS"

        if component in self._database_components():
            return "DATABASE"

        if component in self._network_components():
            return "NETWORK"

        return "APPLICATION"

    def _database_components(self) -> set[str]:
        return {
            "postgres-primary",
            "redis-cache",
        }

    def _network_components(self) -> set[str]:
        return {
            "service-mesh",
            "api-gateway",
        }

    # ============================================================
    # PRIMARY VALUE
    # ============================================================

    def _extract_primary_value(
        self,
        data: Any,
    ) -> Any:
        """
        Extract one representative value from evidence.

        The complete evidence remains available in `evidence`.
        """

        if not isinstance(data, dict):
            return None

        preferred_keys = [
            "error_rate",
            "latency_ms",
            "query_latency_ms",
            "packet_loss_percent",
            "cpu_percent",
            "memory_percent",
            "lock_waits",
            "replication_lag_ms",
            "queue_depth",
            "connection_pool_used",
        ]

        for key in preferred_keys:

            if key in data and data[key] is not None:
                return data[key]

        return None

    # ============================================================
    # EXPECTED VALUE
    # ============================================================

    def _expected_value(
        self,
        category: str,
        data: Any,
    ) -> str | None:
        """
        Provide a baseline expectation when the evidence contains
        a directly comparable operational value.
        """

        if not isinstance(data, dict):
            return None

        if category == "DATABASE":

            if data.get("query_plan") is not None:
                return "indexed"

            if data.get("index_status") is not None:
                return "valid"

            if data.get("lock_waits") is not None:
                return "0"

            if (
                data.get("connection_pool_used")
                is not None
                and data.get("connection_pool_size")
                is not None
            ):
                return (
                    f"< {data['connection_pool_size']}"
                )

        if category == "NETWORK":

            if data.get("packet_loss_percent") is not None:
                return "0%"

            if data.get("connection_resets") is not None:
                return "0"

        if category == "INFRASTRUCTURE":

            if data.get("pods_restarting") is not None:
                return "0"

        return None

    # ============================================================
    # CONFIDENCE
    # ============================================================

    def _calculate_confidence(
        self,
        data: Any,
    ) -> float:
        """
        Assign confidence to the evidence representation.

        This is evidence confidence, NOT root-cause confidence.
        """

        if isinstance(data, dict):

            abnormal_indicators = [
                "status",
                "error_rate",
                "latency_ms",
                "query_latency_ms",
                "packet_loss_percent",
                "connection_resets",
                "lock_waits",
                "replication_lag_ms",
                "cpu_percent",
                "memory_percent",
                "queue_depth",
            ]

            observed = 0

            for key in abnormal_indicators:

                if key in data and data[key] is not None:
                    observed += 1

            if observed >= 3:
                return 0.95

            if observed >= 1:
                return 0.85

        return 0.75