from pathlib import Path
from aius.db import DB


def initialize(db_path: Path) -> int:
    if db_path.exists():
        return -1

    DB(db_path=db_path)
    return 0
