from backend.database import SessionLocal
from backend.repository import IncidentRepository


def main() -> None:
    db = SessionLocal()

    try:
        repository = IncidentRepository(db)

        incident = repository.create_incident(
            incident_id="TEST-PERSISTENCE-001",
            incident_type="DATABASE",
            status="GENERATED",
            severity="MEDIUM",
            raw_data={
                "test": True,
                "message": "PostgreSQL persistence test",
            },
        )

        print("Created:")
        print(incident.incident_id)

        fetched = repository.get_incident("TEST-PERSISTENCE-001")

        print("Fetched:")
        print(fetched.incident_id if fetched else None)

    finally:
        db.close()


if __name__ == "__main__":
    main()