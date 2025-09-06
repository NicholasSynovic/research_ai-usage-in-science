from json import dumps

from pandas import DataFrame, Series
from progress.bar import Bar
from requests import Response, get

import aius


class OpenAlex:
    def __init__(self, email: str, papers_df: DataFrame) -> None:
        # Instantiate class variables
        self.email: str = email
        self.papers_df: DataFrame = papers_df

        # Create a list of DataFrame chunks to iterate through
        self.papers_df_list: list[DataFrame] = [
            self.papers_df[i : i + 50]
            for i in range(
                0,
                len(self.papers_df),
                50,
            )
        ]

    def _get_request(self, dois: Series) -> Response:
        return get(
            url=f"https://api.openalex.org/works?per-page=100&mailto={self.email}&filter=doi:{'|'.join(dois)}",
            timeout=aius.GET_TIMEOUT,
        )

    def _get_topics(self, topics: list[dict[str, dict]]) -> tuple:
        topic_0: str | None = None
        topic_1: str | None = None
        topic_2: str | None = None

        counter: int = 0
        topic: dict
        for topic in topics:
            if counter == 0:
                topic_0 = topic["field"]["display_name"]
            elif counter == 1:
                topic_1 = topic["field"]["display_name"]
            else:
                topic_2 = topic["field"]["display_name"]

            counter += 1

        return (topic_0, topic_1, topic_2)

    def get_metadata(self) -> DataFrame:
        # Create data object
        data: dict[str, list] = {
            "paper_id": [],
            "url": [],
            "status_code": [],
            "cited_by_count": [],
            "topic_0": [],
            "topic_1": [],
            "topic_2": [],
            "json": [],
            "open_access": [],
        }

        # Get the maximum of the bar
        bar_max: int = len(self.papers_df_list)

        with Bar("Calling OpenAlex REST API... ", max=bar_max) as bar:
            # Iterate through the list of DataFrames
            df_chunk: DataFrame
            for df_chunk in self.papers_df_list:
                resp: Response = self._get_request(dois=df_chunk["doi"])

                result: dict
                for result in resp.json()["results"]:
                    # Get the number of papers that cite this paper
                    cited_by_count: int = result["cited_by_count"]

                    # Get the doi of the paper
                    doi: str = result["doi"]

                    # Map DOI to paper ID
                    paper_id: int = df_chunk.loc[df_chunk["doi"] == doi].index[0]

                    # Get OpenAlex assigned paper topics
                    topics: list[dict[str, dict[str, str]]] = result["topics"]
                    topic_0, topic_1, topic_2 = self._get_topics(topics=topics)

                    # Get open access status from the first location
                    open_access: bool = result["locations"][0]["is_oa"]

                    # Store data
                    data["paper_id"].append(paper_id)
                    data["url"].append(resp.url)
                    data["status_code"].append(resp.status_code)
                    data["cited_by_count"].append(cited_by_count)
                    data["topic_0"].append(topic_0)
                    data["topic_1"].append(topic_1)
                    data["topic_2"].append(topic_2)
                    data["json"].append(dumps(obj=result))
                    data["open_access"].append(open_access)

                bar.next()

        return DataFrame(data=data)
