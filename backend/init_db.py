from backend.database import engine
from backend.models import Base


def init_database() -> None:
    Base.metadata.create_all(bind=engine)
    print("PIRA database tables created successfully.")


if __name__ == "__main__":
    init_database()