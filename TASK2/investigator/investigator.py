from models.alert import IncidentAlert
from TASK2.models.investigation import InvestigationCard


class Investigator:
    """
    Task 2 Investigation Agent.

    Responsibilities:
    - Receive an IncidentAlert from Task 1.
    - Identify the affected component.
    - Select relevant Task 3 diagnostic tools.
    - Follow observable evidence to related components.
    - Collect investigation evidence.
    - Build an InvestigationCard for Task 4.

    Important:
    - Task 2 does NOT receive the simulator's hidden root cause.
    - Task 2 does NOT access SimulatedFault.
    - Task 2 does NOT perform RCA.
    - Task 2 does NOT perform remediation.

    Task 2 only collects and organizes evidence.
    """

    def __init__(self, tools) -> None:
        """
        Initialize the investigator with the Task 3 ToolRegistry.
        """
        self.tools = tools

    def investigate(
        self,
        alert: IncidentAlert,
    ) -> InvestigationCard:
        """
        Investigate an incident using Task 3 diagnostic tools.

        The investigator first examines the affected component and
        then follows relevant observable relationships to additional
        components.

        Args:
            alert:
                IncidentAlert received from Task 1.

        Returns:
            InvestigationCard containing observations and evidence.
        """

        evidence = []
        current_state = {}

        component = alert.affected_component

        # --------------------------------------------------------
        # PRIMARY COMPONENT
        # --------------------------------------------------------

        primary_evidence, primary_state = (
            self._investigate_component(component)
        )

        evidence.extend(primary_evidence)
        current_state = primary_state

        # --------------------------------------------------------
        # RELATED COMPONENTS
        # --------------------------------------------------------

        related_components = self._find_related_components(
            alert
        )

        investigated_components = {component}

        for related_component in related_components:

            if related_component in investigated_components:
                continue

            related_evidence, _ = self._investigate_component(
                related_component
            )

            evidence.extend(related_evidence)

            investigated_components.add(
                related_component
            )

        # --------------------------------------------------------
        # BUILD INVESTIGATION CARD
        # --------------------------------------------------------

        return InvestigationCard(
            incident_id=alert.incident_id,
            timestamp=alert.timestamp,
            incident_type=alert.incident_type,
            affected_component=component,
            technology_stack=alert.technology_stack,
            observed_symptoms=alert.symptoms,
            evidence=evidence,
            current_state=current_state,
        )

    # ============================================================
    # COMPONENT INVESTIGATION
    # ============================================================

    def _investigate_component(
        self,
        component: str,
    ) -> tuple[list[dict], dict]:

        evidence = []
        current_state = {}

        # --------------------------------------------------------
        # SERVICE
        # --------------------------------------------------------

        if component in self.tools.state.services:

            metrics = self.tools.metrics.service_metrics(
                component
            )

            logs = self.tools.logs.search(
                component
            )

            evidence.append(
                {
                    "source": "metrics",
                    "component": component,
                    "data": metrics,
                }
            )

            evidence.append(
                {
                    "source": "logs",
                    "component": component,
                    "data": logs,
                }
            )

            current_state = metrics

            return evidence, current_state

        # --------------------------------------------------------
        # DATABASE
        # --------------------------------------------------------

        if component in self.tools.state.databases:

            metrics = self.tools.metrics.database_metrics(
                component
            )

            diagnostics = self.tools.database.inspect(
                component
            )

            logs = self.tools.logs.search(
                component
            )

            evidence.append(
                {
                    "source": "database_metrics",
                    "component": component,
                    "data": metrics,
                }
            )

            evidence.append(
                {
                    "source": "database_diagnostics",
                    "component": component,
                    "data": diagnostics,
                }
            )

            evidence.append(
                {
                    "source": "logs",
                    "component": component,
                    "data": logs,
                }
            )

            current_state = diagnostics

            return evidence, current_state

        # --------------------------------------------------------
        # NETWORK
        # --------------------------------------------------------

        if component in self.tools.state.network:

            diagnostics = self.tools.network.inspect(
                component
            )

            logs = self.tools.logs.search(
                component
            )

            evidence.append(
                {
                    "source": "network_diagnostics",
                    "component": component,
                    "data": diagnostics,
                }
            )

            evidence.append(
                {
                    "source": "logs",
                    "component": component,
                    "data": logs,
                }
            )

            current_state = diagnostics

            return evidence, current_state

        # --------------------------------------------------------
        # INFRASTRUCTURE
        # --------------------------------------------------------

        if component in self.tools.state.infrastructure:

            diagnostics = (
                self.tools.infrastructure.inspect(
                    component
                )
            )

            logs = self.tools.logs.search(
                component
            )

            evidence.append(
                {
                    "source": "infrastructure_diagnostics",
                    "component": component,
                    "data": diagnostics,
                }
            )

            evidence.append(
                {
                    "source": "logs",
                    "component": component,
                    "data": logs,
                }
            )

            current_state = diagnostics

            return evidence, current_state

        # --------------------------------------------------------
        # DEPENDENCY
        # --------------------------------------------------------

        if component in self.tools.state.dependencies:

            metrics = self.tools.metrics.dependency_metrics(
                component
            )

            logs = self.tools.logs.search(
                component
            )

            evidence.append(
                {
                    "source": "dependency_metrics",
                    "component": component,
                    "data": metrics,
                }
            )

            evidence.append(
                {
                    "source": "logs",
                    "component": component,
                    "data": logs,
                }
            )

            current_state = metrics

            return evidence, current_state

        # --------------------------------------------------------
        # UNKNOWN
        # --------------------------------------------------------

        evidence.append(
            {
                "source": "investigator",
                "component": component,
                "data": {
                    "message": (
                        "No diagnostic source found "
                        f"for component: {component}"
                    )
                },
            }
        )

        return evidence, current_state

    # ============================================================
    # RELATED COMPONENT DISCOVERY
    # ============================================================

    def _find_related_components(
        self,
        alert: IncidentAlert,
    ) -> list[str]:
        """
        Determine which additional components should be inspected.

        This method does NOT use the hidden root cause.

        It only uses:
            - incident type
            - affected component
            - observable infrastructure relationships
            - generic investigation rules
        """

        component = alert.affected_component

        related = []

        # --------------------------------------------------------
        # SERVICE-RELATED INVESTIGATION
        # --------------------------------------------------------

        if component in self.tools.state.services:

            if alert.incident_type in (
                "HIGH_ERROR_RATE",
                "APPLICATION",
            ):

                related.extend(
                    self.tools.state.dependencies.keys()
                )

                related.extend(
                    self.tools.state.databases.keys()
                )

            elif alert.incident_type == "API_LATENCY":

                related.extend(
                    self.tools.state.dependencies.keys()
                )

                related.extend(
                    self.tools.state.databases.keys()
                )

                related.extend(
                    self.tools.state.network.keys()
                )

            else:

                related.extend(
                    self.tools.state.dependencies.keys()
                )

        # --------------------------------------------------------
        # DATABASE-RELATED INVESTIGATION
        # --------------------------------------------------------

        elif component in self.tools.state.databases:

            if alert.incident_type in (
                "DATABASE",
                "API_LATENCY",
                "HIGH_ERROR_RATE",
            ):

                related.extend(
                    self.tools.state.services.keys()
                )

        # --------------------------------------------------------
        # NETWORK-RELATED INVESTIGATION
        # --------------------------------------------------------

        elif component in self.tools.state.network:

            if alert.incident_type in (
                "NETWORK",
                "API_LATENCY",
            ):

                related.extend(
                    self.tools.state.services.keys()
                )

        # --------------------------------------------------------
        # INFRASTRUCTURE-RELATED INVESTIGATION
        # --------------------------------------------------------

        elif component in self.tools.state.infrastructure:

            if alert.incident_type in (
                "INFRASTRUCTURE",
                "APPLICATION",
                "API_LATENCY",
                "HIGH_ERROR_RATE",
            ):

                related.extend(
                    self.tools.state.services.keys()
                )

        # --------------------------------------------------------
        # DEPENDENCY-RELATED INVESTIGATION
        # --------------------------------------------------------

        elif component in self.tools.state.dependencies:

            related.extend(
                self.tools.state.services.keys()
            )

        # --------------------------------------------------------
        # REMOVE DUPLICATES
        # --------------------------------------------------------

        unique_related = []

        for item in related:

            if item == component:
                continue

            if item not in unique_related:
                unique_related.append(item)

        return unique_related