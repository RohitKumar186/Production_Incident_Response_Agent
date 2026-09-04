from pathlib import Path


# ---------------------------------------------------------
# TASK 3 ROOT DIRECTORY
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------
# DATA DIRECTORY
# ---------------------------------------------------------

DATA_DIR = BASE_DIR / "data"


# ---------------------------------------------------------
# DATA SOURCE FILES
# ---------------------------------------------------------

LOGS_FILE = DATA_DIR / "logs.json"
METRICS_FILE = DATA_DIR / "metrics.json"
DATABASE_FILE = DATA_DIR / "database.json"
NETWORK_FILE = DATA_DIR / "network.json"