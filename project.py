import csv
import os
from task1 import task1_main
from task2 import task2_main
from task3 import task3_main 
from typing import Iterable, List

# friendly names for csv's
ORIGINAL_BIO = "olympic_athlete_bio.csv"
ORIGINAL_EVENTS = "olympic_athlete_event_results.csv"
ORIGINAL_COUNTRY = "olympics_country.csv"
ORIGINAL_GAMES = "olympics_games.csv"

#NOT ALL JUST FOR TESTING
PARIS_ATHLETES = os.path.join("paris", "athletes.csv")
PARIS_MEDALLISTS = os.path.join("paris", "medallists.csv")
PARIS_NOCS = os.path.join("paris", "nocs.csv")

NEW_BIO = "new_olympic_athlete_bio.csv"
NEW_EVENTS = "new_olympic_athlete_event_results.csv"
NEW_COUNTRY = "new_olympics_country.csv"
NEW_GAMES = "new_olympics_games.csv"
NEW_TALLY = "new_medal_tally.csv"

TALLY_HEADER = [
    "edition",
    "edition_id",
    "Country",
    "NOC",
    "number_of_athletes",
    "gold_medal_count",
    "silver_medal_count",
    "bronze_medal_count",
    "total_medals",
]

def read_csv(path: str) -> List[List[str]]:
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.reader(fh))

def write_csv(path: str, rows: Iterable[Iterable[str]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        for row in rows:
            writer.writerow(list(row))

#new func added FOR TESTING
def validate_paris_files() -> None:
    paris_files = {
        "athletes": PARIS_ATHLETES,
        "medallists": PARIS_MEDALLISTS,
        "nocs": PARIS_NOCS,
    }
    for name, path in paris_files.items():
        rows = read_csv(path)
        if not rows:
            print(f"[warn] Paris {name} missing or empty: {path}")
        else:
            print(f"[ok] Paris {name} has {len(rows)-1} data rows (header excluded).")

def with_age_column(event_rows: List[List[str]]) -> List[List[str]]:
    if not event_rows:
        return [["age"]]
    header = list(event_rows[0])
    header_lower = [h.strip().lower() for h in header]
    if "age" not in header_lower:
        header.append("age")
    result: List[List[str]] = [header]
    for row in event_rows[1:]:
        result.append(list(row) + [""])
    return result

def build_new_outputs() -> None:
    # keep baseline behavior
    bio_rows = read_csv(ORIGINAL_BIO)
    write_csv(NEW_BIO, bio_rows if bio_rows else [])

    event_rows = read_csv(ORIGINAL_EVENTS)
    if event_rows:
        write_csv(NEW_EVENTS, with_age_column(event_rows))
    else:
        write_csv(NEW_EVENTS, [["age"]])

    country_rows = read_csv(ORIGINAL_COUNTRY)
    write_csv(NEW_COUNTRY, country_rows if country_rows else [])

    games_rows = read_csv(ORIGINAL_GAMES)
    write_csv(NEW_GAMES, games_rows if games_rows else [])

def write_tally_header() -> None:
    write_csv(NEW_TALLY, [TALLY_HEADER])

def main() -> None:
    print("Stage B: validating Paris sources...")
    validate_paris_files()
    build_new_outputs()
    write_tally_header()
    print("Stage B complete.")

if __name__ == "__main__":
    task1_main()
    task2_main()
    task3_main()
