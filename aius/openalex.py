"""
Get paper metdata from OpenAlex by DOI.

Copyright 2025 (C) Nicholas M. Synovic

"""

from json import dumps

from pandas import DataFrame, Series, Timestamp
from progress.bar import Bar
from requests import Response, Session
from requests.adapters import HTTPAdapter, Retry

import aius


class OpenAlex:
    def __init__(self, email: str, doi_df: DataFrame) -> None:
        # Instantiate class variables
        self.email: str = email.lower()
        self.plos_paper_id_map: DataFrame = (
            doi_df.copy().reset_index(names="plos_paper_id").set_index(keys="doi")
        )

        # Custom HTTPS session with exponential backoff enabled
        self.session: Session = Session()
        self.session.mount(
            "https://",
            HTTPAdapter(
                max_retries=Retry(total=5, backoff_factor=1),
            ),
        )

        # Create a list of DataFrame chunks to iterate through
        chunk_size: int = 50
        doi_df_size: int = doi_df.shape[0]
        chunked_dois: list[Series] = [
            doi_df.iloc[range(i, min(i + chunk_size, doi_df_size))]["doi"]
            for i in range(0, doi_df_size, chunk_size)
        ]

        # Create URLs to call
        self.urls: list[str] = [
            f"https://api.openalex.org/works?per-page=100&mailto={self.email}&filter=doi:{'|'.join(dois)}"
            for dois in chunked_dois
        ]

        # Get paper metadata from OpenAlex
        self.metadata: DataFrame = self.get_metadata()

    @staticmethod
    def extract_topics(topics: list[dict[str, dict]]) -> tuple:
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

    def get_metadata(self) -> DataFrame:
        # Create data object
        data: dict[str, list] = {
            "doi": [],  # This will be used to map plos_paper_id to metadata
            "json": [],
            "cited_by_count": [],
            "open_access": [],
            "topic_0": [],
            "topic_1": [],
            "topic_2": [],
            "url": [],
            "timestamp": [],
        }

        # Get the number of URLs to request
        url_count: int = len(self.urls)

        with Bar("Calling OpenAlex REST API... ", max=url_count) as bar:
            # Iterate through the list of DataFrames
            url: str
            for url in self.urls:
                timestamp: Timestamp = Timestamp.utcnow()

                # Send a GET request to OpenAlex
                resp: Response = self.session.get(
                    url=url,
                    timeout=aius.GET_TIMEOUT,
                )

                # Parse each result in the JSON
                result: dict
                for result in resp.json()["results"]:
                    # Get the doi of the paper
                    doi: str = result["doi"]

                    # Get the number of papers that cite this paper
                    cited_by_count: int = result["cited_by_count"]

                    # Get open access status from the first location
                    open_access: bool = result["locations"][0]["is_oa"]

                    # Get OpenAlex assigned paper topics
                    topics: list[dict[str, dict[str, str]]] = result["topics"]
                    topic_0, topic_1, topic_2 = self.extract_topics(topics=topics)

                    # Store data
                    data["doi"].append(doi)
                    data["json"].append(dumps(obj=result))
                    data["cited_by_count"].append(cited_by_count)
                    data["open_access"].append(open_access)
                    data["topic_0"].append(topic_0)
                    data["topic_1"].append(topic_1)
                    data["topic_2"].append(topic_2)
                    data["url"].append(resp.url)
                    data["timestamp"].append(timestamp)

                bar.next()

        # Create a DataFrame of the results and map plos_paper_id to doi column
        return (
            DataFrame(data=data)
            .join(self.plos_paper_id_map, on="doi")
            .drop(columns="doi")
        )
