import time
from collections.abc import Callable

from generator.incident_generator import IncidentGenerator


class IncidentScheduler:
    """
    Generates one independent incident per configured interval.

    Every incident starts from a clean healthy infrastructure state.

    Default interval:
        600 seconds = 10 minutes
    """

    def __init__(
        self,
        generator: IncidentGenerator,
        interval_seconds: int = 600,
        on_incident: Callable | None = None,
    ) -> None:
        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be greater than zero")

        self.generator = generator
        self.interval_seconds = interval_seconds
        self.on_incident = on_incident

    def run_once(self):
        """
        Reset infrastructure to healthy state and generate exactly
        one new incident.
        """

        self.generator.infrastructure.reset()

        incident = self.generator.generate()

        if self.on_incident is not None:
            self.on_incident(incident)

        return incident

    def run_forever(self) -> None:
        """
        Generate one independent incident every interval.

        The first incident is generated immediately.
        Subsequent incidents are generated exactly one interval apart.
        """

        while True:
            self.run_once()
            time.sleep(self.interval_seconds)