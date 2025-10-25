import csv
from pathlib import Path

RESOURCE_DIR = Path(__file__).resolve().parent.parent / "resources"


def load_csv_list(filename: str) -> list[str]:
    """
    Load a single-column CSV into a list of strings.
    """
    filepath = RESOURCE_DIR / filename
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        return [row[0].strip() for row in reader if row]


def get_genres() -> list[str]:
    return load_csv_list("genres_list.csv")


def get_actors() -> list[str]:
    return load_csv_list("actors_list.csv")
