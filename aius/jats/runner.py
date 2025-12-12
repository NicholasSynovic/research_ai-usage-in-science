"""
JATS XML download runner.

Copyright 2025 (C) Nicholas M. Synovic

"""

from logging import Logger
from pathlib import Path

import pandas as pd
from pandas import DataFrame
from requests import Session

from aius.db import DB
from aius.jats import ALL_OF_PLOS_DEFAULT_PATH
from aius.megajournals import MEGAJOURNAL_MAPPING, MegaJournal
from aius.runner import Runner
from aius.util.http_session import HTTPSession


class JATSRunner(Runner):  # noqa: D101
    def __init__(  # noqa: D107
        self,
        db: DB,
        logger: Logger,
        megajournal_name: str,
        plos_zip_fp: Path = ALL_OF_PLOS_DEFAULT_PATH,
    ) -> None:
        super().__init__(name="jats", db=db, logger=logger)
        # Set class constants
        self.plos_zip_fp: Path = plos_zip_fp

        # Custom HTTPS session with exponential backoff enabled
        session_util: HTTPSession = HTTPSession()
        self.timeout: int = session_util.timeout
        self.session: Session = session_util.session

        # Identify which megajournal to use
        # Factory method design pattern
        self.megajournal_name: str = megajournal_name.lower()
        self.logger.info("Journal name: %s", self.megajournal_name)
        self.megajournal: MegaJournal = MEGAJOURNAL_MAPPING[self.megajournal_name](
            logger=self.logger, db=self.db
        )
        self.logger.info("Identified journal as %s", self.megajournal.name)

    def _get_data(self) -> DataFrame:
        # Get data from the database
        sql: str = """
            SELECT ns.doi, a.megajournal, oa.json_data
            FROM natural_science_article_dois ns
            JOIN articles a ON a.doi = ns.doi
            JOIN openalex oa ON oa.doi = ns.doi;
        """
        df: DataFrame = pd.read_sql(sql=sql, con=self.db.engine)

        # Split the dataframe by megajournal
        match self.megajournal_name:
            case "bmj":
                return df[df["megajournal"] == "BMJ"].copy()
            case "f1000":
                return df[df["megajournal"] == "F1000"].copy()
            case "frontiersin":
                return df[df["megajournal"] == "FrontiersIn"].copy()
            case "plos":
                return df[df["megajournal"] == "PLOS"].copy()
            case _:
                return DataFrame()

    def _get_table_row_count(self, table_name: str) -> int:
        row_count: int = self.megajournal.db.get_last_row_id(table_name)
        self.logger.info(
            "%s rows previously existed in table `%s`", row_count, table_name
        )
        return row_count

    def _update_df_index(self, table_row_count: int, df: DataFrame) -> None:
        if table_row_count != 0:
            update_val: int = table_row_count + 1
            self.logger.info("Updating search IDs by %s", update_val)
            df.index += update_val

    def execute(self) -> int:  # noqa: D102
        row_count: int = self._get_table_row_count(table_name="jats")

        df: DataFrame = self._get_data()

        jats_df: DataFrame = self.megajournal.download_jats(
            df=df,
            plos_zip_fp=self.plos_zip_fp,
        )
        self._update_df_index(table_row_count=row_count, df=jats_df)

        self.db.write_dataframe_to_table(table_name="jats", df=jats_df)

        return 0
