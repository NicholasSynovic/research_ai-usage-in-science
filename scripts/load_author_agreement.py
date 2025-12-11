import json
from pathlib import Path

import pandas as pd

from aius.db import DB


class LoadAuthorAgreement:
    def __init__(self, pilot_study_csv: Path, db: DB) -> None:
        # Load CSV file
        self.df: pd.DataFrame = pd.read_csv(
            filepath_or_buffer=pilot_study_csv.resolve(),
        )

        # Format JSON data
        self.df["ptm_name_reuse_type"] = self.df["ptm_name_reuse_type"].apply(
            lambda x: json.dumps(obj=json.loads(s=x))
        )

        # Format binary (True, False) data
        self.df["uses_dl"] = self.df["uses_dl"].astype(dtype=bool)
        self.df["uses_ptms"] = self.df["uses_ptms"].astype(dtype=bool)

        # Get mapping of all PLOS papers
        map_df: pd.DataFrame = pd.read_sql_table(
            table_name="plos_paper_dois",
            con=db.engine,
        )
        map_df = map_df.set_index(keys="doi")

        # Map plos_paper_id to pilot study data
        self.df = self.df.join(other=map_df, on="doi")
        self.df = self.df.drop(columns="doi")

        # Replace empty mappings with -1
        self.df["_id"] = self.df["_id"].fillna(value=-1)

        # Rename column
        self.df = self.df.rename(columns={"_id": "plos_paper_id"})
