"""
OpenAlex metadata search runner.

Copyright 2025 (C) Nicholas M. Synovic

"""

from datetime import datetime, timezone
from logging import Logger
from string import Template

import pandas as pd
from pandas import DataFrame
from progress.bar import Bar
from requests import Response, Session

from aius.db import DB
from aius.openalex import MetadataModel
from aius.runner import Runner
from aius.util.http_session import HTTPSession


class OpenAlexRunner(Runner):  # noqa: D101
    def __init__(  # noqa: D107
        self,
        db: DB,
        logger: Logger,
        email: str,
    ) -> None:
        # Set class constants
        super().__init__(name="openalex", db=db, logger=logger)
        self.email: str = email

        self.search_template: Template = Template(
            template="https://api.openalex.org/works?per-page=100&mailto=${email}&filter=doi:${dois}"
        )

        # Custom HTTPS session with exponential backoff enabled
        session_util: HTTPSession = HTTPSession()
        self.timeout: int = session_util.timeout
        self.session: Session = session_util.session

    def _get_doi_chunks(self, chunk_size: int = 50) -> list[list[str]]:
        # Get all DOIs from the database
        sql: str = "SELECT DISTINCT doi FROM articles;"
        doi_df: DataFrame = pd.read_sql_query(sql=sql, con=self.db.engine)
        doi_list: list[str] = doi_df["doi"].tolist()

        # Format dois
        doi_list = ["https://doi.org/" + doi for doi in doi_list]

        # Chunk dois into groups
        return [doi_list[i : i + 50] for i in range(0, len(doi_list), 50)]

    @staticmethod
    def extract_topics(topics: list[dict[str, dict]]) -> tuple:  # noqa: D102
        topic_0: str | None = None
        topic_1: str | None = None
        topic_2: str | None = None

        for i, topic in enumerate(topics):
            if i == 0:
                topic_0 = topic["field"]["display_name"]
            elif i == 1:
                topic_1 = topic["field"]["display_name"]
            else:
                topic_2 = topic["field"]["display_name"]

        return (topic_0, topic_1, topic_2)

    def search(self) -> list[MetadataModel]:  # noqa: D102
        data: list[MetadataModel] = []

        doi_chunks: list[list[str]] = self._get_doi_chunks()

        with Bar("Searching OpenAlex for DOI metadata...", max=len(doi_chunks)) as bar:
            chunk: list[str]
            for chunk in doi_chunks:
                url: str = self.search_template.substitute(
                    email=self.email,
                    dois="|".join(chunk),
                )
                self.logger.info("Querying %s", url)

                timestamp: float = datetime.now(tz=timezone.utc).timestamp()
                resp: Response = self.session.get(url=url)
                self.logger.debug("Response status code: %s", resp.status_code)

                result: dict
                for result in resp.json()["results"]:
                    topic_0, topic_1, topic_2 = self.extract_topics(
                        topics=result["topics"]
                    )

                    data.append(
                        MetadataModel(
                            timestamp=timestamp,
                            doi=result["doi"].replace("https://doi.org/", ""),
                            cited_by_count=int(result["cited_by_count"]),
                            open_access=result["open_access"]["is_oa"],
                            topic_0=topic_0,
                            topic_1=topic_1,
                            topic_2=topic_2,
                            json_data=result,
                        )
                    )

                bar.next()

        return data

    def execute(self) -> int:  # noqa: D102
        # Get the current row count of the `openalex` table to ensure that the
        # SQL Unique constraint is not violated by updating DataFrame index
        # later
        search_table_row_count: int = self.db.get_last_row_id(table_name="openalex")

        # Conduct searches
        self.logger.info("Executing OpenAlex search")
        searches: list[MetadataModel] = self.search()
        self.logger.info("Searched %s documents", len(searches))

        # Create DataFrame of searches
        self.logger.info(msg="Preparing searches for database write")
        searches_df: DataFrame = pd.concat(
            objs=[mm.to_df for mm in searches],
            ignore_index=True,
        )

        # Update unique search IDs
        if search_table_row_count != 0:
            update_val: int = search_table_row_count + 1
            self.logger.info("Updating search IDs by %s", update_val)
            searches_df.index += update_val

        # Write DataFrame to the database
        self.db.write_dataframe_to_table(table_name="openalex", df=searches_df)

        return 0
