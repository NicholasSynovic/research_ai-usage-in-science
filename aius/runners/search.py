from logging import Logger

import pandas
from pandas import DataFrame

from aius.db import DB
from aius.runners import Runner
from aius.search.bmj import BMJ
from aius.search.f1000 import F1000
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
    def __init__(self, db: DB, logger: Logger, megajournal_name: str) -> None:
        # Set constants
        super().__init__(name="search", db=db, logger=logger)
        self.megajournal_name: str = megajournal_name.lower()
        self.logger.info("Journal name: %s", self.megajournal_name)

        # Identify which megajournal to use
        self.megajournal: MegaJournal
        match self.megajournal_name:
            case "bmj":
                self.megajournal = BMJ(logger=self.logger, db=self.db)
            case "frontiersin":
                self.megajournal = FrontiersIn(logger=self.logger, db=self.db)
            case "f1000":
                self.megajournal = F1000(logger=self.logger, db=self.db)
            case "plos":
                self.megajournal = PLOS(logger=self.logger, db=self.db)

        self.logger.info("Identified journal as %s", self.megajournal.name)

    def execute(self) -> int:
        # Get the current row count of the `searches` table to ensure that the
        # SQL Unique constraint is not violated by updating DataFrame index
        # later
        search_table_row_count: int = self.megajournal.db.get_last_row_id(
            table_name="searches"
        )
        article_table_row_count: int = self.megajournal.db.get_last_row_id(
            table_name="articles"
        )

        # Conduct searches
        self.logger.info("Executing %s search", self.megajournal.name)
        searches: list[SearchModel] = self.megajournal.search()
        self.logger.info(
            "Searched %s queries in %s",
            len(searches),
            self.megajournal.name,
        )

        # Parse searches for articles
        self.logger.info("Executing %s article extraction", self.megajournal.name)
        articles: list[ArticleModel] = self.megajournal.parse_response(
            responses=searches
        )
        self.logger.info(
            "Extracted %s from %s",
            len(articles),
            self.megajournal.name,
        )

        # Create DataFrame of searches
        self.logger.info(msg="Preparing searches for database write")
        searches_df: DataFrame = pandas.concat(
            objs=[search_model_to_df(sm=sm) for sm in searches],
            ignore_index=True,
        )
        self.logger.debug("Data: %s", searches_df)

        # Create DataFrame of articles
        self.logger.info(msg="Preparing articles for database write")
        articles_df: DataFrame = pandas.concat(
            objs=[article_model_to_df(am=am) for am in articles],
            ignore_index=True,
        )
        self.logger.debug("Data: %s", articles_df)

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
            self.logger.info("Updating search IDs by %s", update_val)
            searches_df.index = searches_df.index + update_val

        # Update unique article IDs
        if article_table_row_count != 0:
            update_val: int = article_table_row_count + 1
            self.logger.info(msg=f"Updating search IDs by {update_val}")
            articles_df.index = articles_df.index + update_val

        # Write DataFrames to the database
        self.db.write_dataframe_to_table(table_name="searches", df=searches_df)
        self.db.write_dataframe_to_table(table_name="articles", df=articles_df)

        return 0
