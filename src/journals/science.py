from pathlib import Path
from string import Template
from typing import List
from urllib.parse import quote_plus

from pandas import DataFrame


class Science:
    def __init__(self) -> None:
        self.journalName: str = "Science"
        self.searchURLTemplate: Template = Template(
            template="https://www.science.org/action/doSearch?AllField=${query}&ConceptID=505154&ConceptID=505172&AfterYear=${year}&BeforeYear=${year}&queryID=8%2F7249304983&sortBy=Earliest"  # noqa: E501
        )  # noqa: E501
        self.message: str = """
Due to section 6 subsection b of the AAAS Science terms of service
(availible here: https://www.science.org/content/page/terms-service), we are
unable to provide an automatic tool to extract or analyze the contents of the
AAAS Science website (https://www.science.org).

Therefore, we will not be providing a tool, the information to produce such a
tool, or the raw, untransformed content of the AAAS Science website in any
form.

However, for manual analysis, the following URLs we do provide all of the
necessary URLs to reproduce our work are now stored in `./science_urls.json`.
"""

    def generateURLs(
        self,
        years: List[int],
        queries: List[str],
        fp: Path = Path("science_urls.json"),
    ) -> None:
        json: dict[str, List[str]] = {}

        query: str
        for query in queries:
            key = query.replace('"', "")
            json[key] = []

            year: int
            for year in years:
                json[key].append(
                    self.searchURLTemplate.substitute(
                        year=year,
                        query=quote_plus(
                            string=query,
                        ),
                    )
                )

        df: DataFrame = DataFrame(data=json)
        df.index += 2014
        df.to_json(path_or_buf=fp, indent=4, index=False)
