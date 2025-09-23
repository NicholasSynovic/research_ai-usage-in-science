import zipfile
from pathlib import Path

import pandas
from pandas import DataFrame

from aius.db import DB

all_of_plos_archive: Path = Path("../data/all_of_plos.zip").resolve()
db: DB = DB(db_path=Path())
