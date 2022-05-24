import json
from pathlib import Path


def load_config(filename: str) -> dict:
    """Returns data from `.json` file."""
    file = Path(f"config/{filename}.json")
    data = file.open("r", encoding="UTF-8")
    return json.load(data)
