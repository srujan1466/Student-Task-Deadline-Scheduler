import json
from pathlib import Path

DATA_FILE = Path(__file__).parent / "data" / "tasks.json"


def load_tasks():
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_tasks(tasks):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = DATA_FILE.with_suffix(".tmp")

    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=4)

    temporary_file.replace(DATA_FILE)