from json import dumps
from logging import Logger

import pandas
from pandas import DataFrame

from aius.db import DB
from aius.runners.runner import Runner
from aius.search.frontiersin import FrontiersIn
from aius.search.megajournal import (
    MegaJournal,
    SearchModel,
    search_model_to_df,
)
from aius.search.plos import PLOS


class SearchRunner(Runner):
    def __init__(self, logger: Logger, db: DB, journal: str) -> None:
        self.logger: Logger = logger

        self.journal: MegaJournal | None
        match journal:
            case "plos":
                self.journal = PLOS(logger=self.logger, db=db)
            case "frontiersin":
                self.journal = FrontiersIn(logger=self.logger, db=db)
            case _:
                self.journal = None

        if self.journal is None:
            self.logger.error(msg=f"Journal is set to None (journal={journal})")
        else:
            self.logger.info(msg=f"Identified journal as {self.journal.megajournal}")

    def _write_data_to_table(self, table: str, data: DataFrame) -> None:
        self.logger.info(msg=f"Writing data to the `{table}` table")
        self.logger.debug(msg=f"Data: {data}")
        data.to_sql(
            name=table,
            con=self.journal.db.engine,
            if_exists="append",
            index=True,
            index_label="_id",
        )
        self.logger.info(msg=f"Wrote data to the `{table}` table")

    def execute(self) -> int:
        # Check that the journal is not None
        if self.journal is None:
            self.logger.info(msg="Journal is None. Returning 1")
            return 1

        # Get the current row count of the `searches` table to ensure that the
        # SQL Unique constraint is not violated by updating DataFrame index
        # later
        search_table_row_count: int = self.journal.db.get_last_row_id(
            table_name="searches"
        )

        # Conduct searches
        self.logger.info(msg=f"Executing {self.journal.megajournal} search")
        searches: list[SearchModel] = self.journal.search()
        self.logger.info(
            msg=f"Searched {len(searches)} queries in {self.journal.megajournal}"
        )

        # Create DataFrame of searches
        searches_df: DataFrame = pandas.concat(
            objs=[search_model_to_df(sm=sm) for sm in searches],
            ignore_index=True,
        )

        if search_table_row_count != 0:
            searches_df.index = searches_df.index + search_table_row_count + 1

        # Write DataFrame to the database
        self._write_data_to_table(table="searches", data=searches_df)

        return 0
