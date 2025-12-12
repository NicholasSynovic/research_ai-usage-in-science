"""
Conduct journal searches.

Copyright 2025 (C) Nicholas M. Synovic

"""

from logging import Logger

import pandas as pd
from pandas import DataFrame

from aius.db import DB
from aius.megajournals import MEGAJOURNAL_MAPPING
from aius.megajournals.megajournal import MegaJournal
from aius.megajournals.models import ArticleModel, SearchModel
from aius.runner import Runner


# Template method design pattern
class SearchRunner(Runner):  # noqa: D101
    def __init__(  # noqa: D107
        self,
        db: DB,
        logger: Logger,
        megajournal_name: str,
    ) -> None:
        # Set constants
        super().__init__(name="search", db=db, logger=logger)

        # Identify which megajournal to use
        # Factory method design pattern
        self.megajournal_name: str = megajournal_name.lower()
        self.logger.info("Journal name: %s", self.megajournal_name)
        self.megajournal: MegaJournal = MEGAJOURNAL_MAPPING[self.megajournal_name](
            logger=self.logger, db=self.db
        )
        self.logger.info("Identified journal as %s", self.megajournal.name)

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

    def search_for_articles(self) -> list[SearchModel]:
        # Get the current row count of the `searches` table to ensure that the
        # SQL Unique constraint is not violated by updating DataFrame index
        # later
        row_count: int = self._get_table_row_count(table_name="searches")

        # Conduct searches
        self.logger.info("Executing %s search", self.megajournal.name)
        searches: list[SearchModel] = self.megajournal.search()
        self.logger.info(
            "Searched %s queries in %s",
            len(searches),
            self.megajournal.name,
        )

        # Create DataFrame of searches
        self.logger.info(msg="Preparing searches for database write")

        searches_df = pd.concat(
            objs=[sm.to_df for sm in searches],
            ignore_index=True,
        )
        self.logger.debug("Search DataFrame: %s", searches_df)

        # Update unique search IDs
        self._update_df_index(table_row_count=row_count, df=searches_df)

        # Write data
        self.db.write_dataframe_to_table(table_name="searches", df=searches_df)

        return searches

    def parse_articles(self, searches: list[SearchModel]) -> None:
        # Get the current row count of the `articles` table to ensure that the
        # SQL Unique constraint is not violated by updating DataFrame index
        # later
        row_count: int = self._get_table_row_count(table_name="articles")

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

        # Create DataFrame of articles
        self.logger.info(msg="Preparing articles for database write")
        articles_df: DataFrame = pd.concat(
            objs=[am.to_df for am in articles],
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

        # Update unique article IDs
        self._update_df_index(table_row_count=row_count, df=articles_df)

        # Write DataFrames to the database
        self.db.write_dataframe_to_table(table_name="articles", df=articles_df)

    def execute(self) -> int:  # noqa: D102
        searches: list[SearchModel] = self.search_for_articles()
        self.parse_articles(searches=searches)

        return 0
