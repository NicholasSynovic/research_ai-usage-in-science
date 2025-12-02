from json import dumps
from logging import Logger

import pandas
from pandas import DataFrame

from aius.db import DB
from aius.runners.runner import Runner
from aius.search.bmj import BMJ
from aius.search.frontiersin import FrontiersIn
from aius.search.megajournal import (
    ArticleModel,
    MegaJournal,
    SearchModel,
    article_model_to_df,
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
            case "bmj":
                self.journal = BMJ(logger=self.logger, db=db)
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
        article_table_row_count: int = self.journal.db.get_last_row_id(
            table_name="articles"
        )

        # Conduct searches
        self.logger.info(msg=f"Executing {self.journal.megajournal} search")
        searches: list[SearchModel] = self.journal.search()
        self.logger.info(
            msg=f"Searched {len(searches)} queries in {self.journal.megajournal}"
        )

        # Parse searches for articles
        self.logger.info(msg=f"Executing {self.journal.megajournal} article extraction")
        articles: list[ArticleModel] = self.journal.parse_response(responses=searches)
        self.logger.info(
            msg=f"Extracted {len(articles)} from {self.journal.megajournal}"
        )

        # Create DataFrame of searches
        self.logger.info(msg="Preparing searches for database write")
        searches_df: DataFrame = pandas.concat(
            objs=[search_model_to_df(sm=sm) for sm in searches],
            ignore_index=True,
        )

        # Create DataFrame of articles
        self.logger.info(msg="Preparing articles for database write")
        articles_df: DataFrame = pandas.concat(
            objs=[article_model_to_df(am=am) for am in articles],
            ignore_index=True,
        )

        # Only keep unique articles by DOI
        self.logger.info(msg="Dropping duplicate DOI entries")
        articles_df = articles_df.drop_duplicates(
            subset="doi",
            keep="first",
            ignore_index=True,
        )
        articles_df = articles_df.drop(columns=["search_id"])

        # Update unique search IDs
        if search_table_row_count != 0:
            update_val: int = search_table_row_count + 1
            self.logger.info(msg=f"Updating search IDs by {update_val}")
            searches_df.index = searches_df.index + update_val

        # Update unique article IDs
        if article_table_row_count != 0:
            update_val: int = article_table_row_count + 1
            self.logger.info(msg=f"Updating search IDs by {update_val}")
            articles_df.index = articles_df.index + update_val

        # Write DataFrames to the database
        self._write_data_to_table(table="searches", data=searches_df)
        self._write_data_to_table(table="articles", data=articles_df)

        return 0
