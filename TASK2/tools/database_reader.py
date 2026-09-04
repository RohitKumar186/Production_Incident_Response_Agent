import json

from config.settings import DATABASE_FILE


def read_database():
    """
    Read database and query performance information.
    """

    with open(DATABASE_FILE, "r", encoding="utf-8") as file:
        database = json.load(file)

    return database