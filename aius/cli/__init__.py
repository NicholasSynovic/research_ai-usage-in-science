from pathlib import Path

# Used for the top level parser
PROGRAM_NAME: str = "AIUS"
PROGRAM_DESCRIPTION: str = "Pre-trained deep learning model reusage in natural science"
PROGRAM_EPILOG: str = "Copyright 2025 (C) Nicholas M. Synovic"

# Common variables for database handling
DB_DEFAULT_NAME: str = "aius.sqlite3"
DB_HELP_MESSAGE: str = "Path to SQLite3 database"
DB_DEFAULT_PATH: Path = Path(f"{DB_DEFAULT_NAME}").resolve()

# Step 0 variables
MIN_YEAR_HELP: str = "Minimum year to search for documents"
MAX_YEAR_HELP: str = "Maximum year to search for documents"

# Step 1 variables
JOURNAL_HELP: str = "Mega-journal to search from"
JOURNAL_CHOICES: list[str] = ["bmj", "f1000", "frontiersin", "peerj", "plos"]
