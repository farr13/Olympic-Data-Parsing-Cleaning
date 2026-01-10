import csv
from datetime import datetime


# --------------------------------------------------------------
# CLASS: DataCleaner
# --------------------------------------------------------------
class DataCleaner:
    """
    Responsible for all data cleaning logic.
    - clean_birthdate: fixes the 'born' column in olympic_athlete_bio.csv
    - clean_competition_date: fixes the 'competition_date' column in olympics_games.csv
    """

    def clean_birthdate(self, date_str):
        """
        Clean a raw birthdate string into the format dd-Mon-yyyy.

        Handles:
          - dd-Mon-yy         (e.g. '04-Apr-49')
          - dd-Mon-yyyy       (e.g. '04-Apr-1949')
          - dd Month yyyy     (e.g. '24 November 1873')
          - dd Mon yyyy       (e.g. '24 Nov 1873')
          - Month yyyy        (e.g. 'July 1882')      -> assume day = 1
          - yyyy              (e.g. '1879')          -> assume 01-Jan-yyyy

        If the value is missing or cannot be parsed, returns an empty string.
        """
        # 1) Handle None and obvious missing markers
        if date_str is None:
            return ""
        s = str(date_str).strip()

        if s == "" or s.lower() in ["unknown", "na", "n/a", "nan", "none"]:
            return ""

        # --------------------------------------------------
        # 2) Case: dd-Mon-yy  (e.g. '04-Apr-49')
        #    We read the 2-digit year ourselves and decide the century.
        # --------------------------------------------------
        parts = s.split("-")
        if len(parts) == 3 and len(parts[2]) == 2 and parts[2].isdigit():
            day_str, mon_str, yy_str = parts
            yy = int(yy_str)

            # Century rule:
            #   00–22  -> 2000–2022
            #   23–99  -> 1923–1999
            if 0 <= yy <= 22:
                full_year = 2000 + yy
            else:
                full_year = 1900 + yy

            try:
                # Rebuild with 4-digit year and parse
                dt = datetime.strptime(f"{day_str}-{mon_str}-{full_year}", "%d-%b-%Y")
                return dt.strftime("%d-%b-%Y")
            except ValueError:
                # If this fails, fall through to other formats
                pass

        # --------------------------------------------------
        # 3) Case: dd-Mon-yyyy (already in target style, but we normalise)
        # --------------------------------------------------
        try:
            dt = datetime.strptime(s, "%d-%b-%Y")
            return dt.strftime("%d-%b-%Y")
        except ValueError:
            pass

        # --------------------------------------------------
        # 4) Case: dd Month yyyy (e.g. '24 November 1873')
        # --------------------------------------------------
        try:
            dt = datetime.strptime(s, "%d %B %Y")
            return dt.strftime("%d-%b-%Y")
        except ValueError:
            pass

        # --------------------------------------------------
        # 5) Case: dd Mon yyyy (e.g. '24 Nov 1873')
        # --------------------------------------------------
        try:
            dt = datetime.strptime(s, "%d %b %Y")
            return dt.strftime("%d-%b-%Y")
        except ValueError:
            pass

        # --------------------------------------------------
        # 6) Case: Month yyyy (e.g. 'July 1882', 'Apr 1881')
        #    Reasonable estimate: assume day = 1.
        # --------------------------------------------------
        try:
            dt = datetime.strptime(s, "%B %Y")   # long month name
            dt = dt.replace(day=1)
            return dt.strftime("%d-%b-%Y")
        except ValueError:
            pass

        try:
            dt = datetime.strptime(s, "%b %Y")   # short month name
            dt = dt.replace(day=1)
            return dt.strftime("%d-%b-%Y")
        except ValueError:
            pass

        # --------------------------------------------------
        # 7) Case: year only (e.g. '1879')
        #    Reasonable estimate: 01-Jan-<year>.
        # --------------------------------------------------
        if s.isdigit() and len(s) == 4:
            try:
                year = int(s)
                dt = datetime(year, 1, 1)
                return dt.strftime("%d-%b-%Y")
            except ValueError:
                return ""

        # If none of the patterns match, treat as missing.
        return ""

    def clean_competition_date(self, date_str, year):
        """
        Clean a competition_date value using the given year.

        The raw values look like:
            '6 – 13 April'
            '14 May – 28 October'
            '1 July – 26 November'
            '—'  (dash only, no dates)

        Output format must be:
            'dd-Mon-yyyy to dd-Mon-yyyy'

        If only one side is given a month (e.g. '6 – 13 April'),
        we assume the month from the right side also applies to the left.
        If the value cannot be parsed, returns an empty string.
        """
        # Handle missing values
        if date_str is None or str(date_str).strip() == "":
            return ""

        raw = str(date_str).strip()

        # Normalise all dash-like characters to a simple hyphen
        #    The file uses en dash, em dash, minus sign, etc.
        for dash in ["–", "—", "−"]:
            raw = raw.replace(dash, "-")

        # Turn hyphens into " to " (our range separator)
        raw = raw.replace(" - ", " to ")
        raw = raw.replace("-", " to ")

        # Collapse extra spaces
        while "  " in raw:
            raw = raw.replace("  ", " ")

        # If there's no ' to ', treat as a single date
        if " to " not in raw:
            return self._format_single_date(raw, year)

        # Split into start and end parts (once)
        start_str, end_str = raw.split(" to ", 1)
        start_str = start_str.strip()
        end_str = end_str.strip()

        # Handle cases like '6 – 13 April':
        #    start_str = '6', end_str = '13 April'
        #    -> borrow the month from end_str so start becomes '6 April'.
        end_parts = end_str.split()
        if len(start_str.split()) == 1 and len(end_parts) == 2:
            month = end_parts[1]
            start_str = f"{start_str} {month}"

        # Format both start and end as dd-Mon-yyyy
        start_clean = self._format_single_date(start_str, year)
        end_clean = self._format_single_date(end_str, year)

        # If either side fails, treat as missing
        if not start_clean or not end_clean:
            return ""

        return f"{start_clean} to {end_clean}"

    def _format_single_date(self, s, year):
        """
        Helper for competition dates.

        Input examples (with year added separately):
            '6 April'  + 1896  -> '06-Apr-1896'
            '13 October' + 1896 -> '13-Oct-1896'
        """
        # First try full month name (e.g. 'April')
        try:
            dt = datetime.strptime(f"{s} {year}", "%d %B %Y")
        except ValueError:
            # Then try abbreviated month name (e.g. 'Apr')
            try:
                dt = datetime.strptime(f"{s} {year}", "%d %b %Y")
            except ValueError:
                return ""

        return dt.strftime("%d-%b-%Y")


# --------------------------------------------------------------
# CLASS: FileProcessor
# --------------------------------------------------------------
class FileProcessor:
    """
    Handles reading/writing CSV files and delegates actual cleaning
    to the DataCleaner class.
    """

    def __init__(self):
        self.cleaner = DataCleaner()

    def process_athlete_bio(self, input_file, output_file):
        """
        Reads olympic_athlete_bio.csv and writes new_olympic_athlete_bio.csv.

        For each row:
          - Cleans the 'born' column using DataCleaner.clean_birthdate().
          - Copies all other columns unchanged.
        """
        with open(input_file, newline="", encoding="utf-8") as infile, \
             open(output_file, "w", newline="", encoding="utf-8") as outfile:

            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
            writer.writeheader()

            for row in reader:
                # Clean the 'born' value
                row["born"] = self.cleaner.clean_birthdate(row.get("born", ""))
                writer.writerow(row)

    def process_games_data(self, input_file, output_file):
        """
        Reads olympics_games.csv and writes new_olympics_games.csv.

        For each row:
          - Cleans the 'competition_date' column using DataCleaner.clean_competition_date(),
            passing in the 'year' column.
          - Copies all other columns unchanged.
        """
        with open(input_file, newline="", encoding="utf-8") as infile, \
             open(output_file, "w", newline="", encoding="utf-8") as outfile:

            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
            writer.writeheader()

            for row in reader:
                year = row.get("year", "")
                competition_raw = row.get("competition_date", "")

                # Clean the competition_date using the year from this row
                cleaned = self.cleaner.clean_competition_date(competition_raw, year)
                row["competition_date"] = cleaned
                writer.writerow(row)


# --------------------------------------------------------------
# MAIN FUNCTION
# --------------------------------------------------------------
def task2_main():
    processor = FileProcessor()

    processor.process_athlete_bio(
        "olympic_athlete_bio.csv",
        "new_olympic_athlete_bio.csv"
    )

    processor.process_games_data(
        "olympics_games.csv",
        "new_olympics_games.csv"
    )

    print("Done cleaning all files.")


# --------------------------------------------------------------
# RUN MAIN
# --------------------------------------------------------------
if __name__ == "__main__":
    main()
