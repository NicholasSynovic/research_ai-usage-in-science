from pathlib import Path

import pandas as pd

from aius.db.db import DB


class LoadPilotStudy:
    def __init__(self, pilot_study_csv: Path, db: DB) -> None:
        # Load CSV file
        self.df: pd.DataFrame = pd.read_csv(
            filepath_or_buffer=pilot_study_csv.resolve(),
        )

        # Get mapping of all PLOS papers
        map_df: pd.DataFrame = pd.read_sql_table(
            table_name="plos_paper_dois",
            con=db.engine,
        )
        map_df["doi"] = map_df["doi"].str.strip(to_strip="https://doi.org/")
        map_df = map_df.set_index(keys="doi")

        # Map plos_paper_id to pilot study data
        self.df = self.df.join(other=map_df, on="doi")
        self.df = self.df.drop(columns="doi")

        # Replace empty mappings with -1
        self.df["_id"] = self.df["_id"].fillna(value=-1)

        # Rename column
        self.df = self.df.rename(columns={"_id": "plos_paper_id"})
