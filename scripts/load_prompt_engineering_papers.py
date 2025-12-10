import pandas as pd

import aius
from aius.db import DB


class LoadPromptEngineeringPapers:
    def __init__(self, db: DB) -> None:
        self.df: pd.DataFrame = aius.LLM_PROMPT_ENGINEERING_PAPERS.copy()

        # Get mapping of all PLOS papers
        map_df: pd.DataFrame = pd.read_sql_table(
            table_name="plos_paper_dois",
            con=db.engine,
        )
        map_df = map_df.set_index(keys="doi")

        # Map plos_paper_id to pilot study data
        self.df = self.df.join(other=map_df, on="doi")
        self.df = self.df.drop(columns="doi")

        # Rename column
        self.df = self.df.rename(columns={"_id": "plos_paper_id"})
