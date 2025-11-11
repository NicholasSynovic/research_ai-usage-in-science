from pathlib import Path


class InitRunner:
    def __init__(self, db_path: Path, min_year: int, max_year: int) -> None:
        # Set constants
        self.db_path: Path = db_path
        self.min_year: int = min_year
        self.max_year: int = max_year

        # Create range of years
        self.year_range: range = range(self.min_year, self.max_year + 1)
