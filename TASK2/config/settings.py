from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent


# Data directory
DATA_DIR = BASE_DIR / "data"


# Data source files
LOGS_FILE = DATA_DIR / "logs.json"
METRICS_FILE = DATA_DIR / "metrics.json"
DATABASE_FILE = DATA_DIR / "database.json"
NETWORK_FILE = DATA_DIR / "network.json"