from pathlib import Path
from aius.db import DB


def initialize(db_path: Path) -> int:
    if db_path.exists():
        return -1

    db: DB = DB(fp=db_path)
    db.createTables()
    db.writeConstants()
    return 0
