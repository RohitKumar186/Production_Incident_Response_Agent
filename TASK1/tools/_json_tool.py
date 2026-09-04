import json
from pathlib import Path
from typing import Any


class JsonTool:
    filename: str

    def __init__(self, data_directory: Path | None = None) -> None:
        root = data_directory or Path(__file__).resolve().parents[1] / "data"
        self.path = root / self.filename

    def read(self) -> dict[str, Any]:
        with self.path.open(encoding="utf-8") as data_file:
            return json.load(data_file)