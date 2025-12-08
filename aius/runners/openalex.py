"""
OpenAlex metadata search runner.

Copyright 2025 (C) Nicholas M. Synovic

"""

from datetime import datetime, timezone
from json import dumps
from logging import Logger
from string import Template

import pandas as pd
from pandas import DataFrame
from progress.bar import Bar
from pydantic import BaseModel
from requests import Response, Session
from requests.adapters import HTTPAdapter, Retry

from aius.db import DB
from aius.runners import Runner


class MetadataModel(BaseModel):  # noqa: D101
    timestamp: float
    doi: str
    cited_by_count: int
    open_access: bool
    topic_0: str | None
    topic_1: str | None
    topic_2: str | None
    json_data: dict


class OpenAlexRunner(Runner):  # noqa: D101
    def __init__(  # noqa: D107
        self,
        logger: Logger,
        email: str,
        db: DB,
    ) -> None:
        # Set class constants
        self.logger: Logger = logger
        self.email: str = email
        self.db: DB = db
        self.search_template: Template = Template(
            template="https://api.openalex.org/works?per-page=100&mailto=${email}&filter=doi:${dois}"
        )

        # Custom HTTPS session with exponential backoff enabled
        self.session: Session = Session()
        self.session.mount(
            "https://",
            HTTPAdapter(
                max_retries=Retry(total=10, backoff_factor=1),
            ),
        )

        # Get all DOIs from the database
        dois: list[str] = [
            "https://doi.org/" + doi
            for doi in pd.read_sql_query(
                sql="SELECT DISTINCT doi FROM articles;", con=self.db.engine
            )["doi"].tolist()
        ]
        self.doi_chunks: list[list[str]] = [
            dois[i : i + 50] for i in range(0, len(dois), 50)
        ]

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

    @staticmethod
    def metadata_model_to_df(mm: MetadataModel) -> DataFrame:  # noqa: D102
        data: dict[str, list] = {
            "timestamp": [mm.timestamp],
            "doi": [mm.doi],
            "cited_by_count": [mm.cited_by_count],
            "open_access": [mm.open_access],
            "topic_0": [mm.topic_0],
            "topic_1": [mm.topic_1],
            "topic_2": [mm.topic_2],
            "json_data": [dumps(obj=mm.json_data)],
        }

        return DataFrame(data=data)

    def search(self) -> list[MetadataModel]:  # noqa: D102
        data: list[MetadataModel] = []

        with Bar(
            "Searching OpenAlex for DOI metadata...", max=len(self.doi_chunks)
        ) as bar:
            chunk: list[str]
            for chunk in self.doi_chunks:
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
            objs=[self.metadata_model_to_df(mm=mm) for mm in searches],
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
