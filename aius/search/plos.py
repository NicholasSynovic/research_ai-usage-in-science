from math import ceil
from string import Template

import pandas as pd
from pandas import DataFrame
from progress.bar import Bar

from aius.search import JournalSearch


class PLOS(JournalSearch):
    def __init__(self) -> None:
        # Initialize class variables
        self.name: str = "plos"

        # Create search URL template
        self.search_url_template: Template = Template(
            template="https://journals.plos.org/plosone/dynamicSearch?filterStartDate=${year}-01-01&filterEndDate=${year}-12-31&resultsPerPage=100&q=${keyword}&sortOrder=DATE_NEWEST_FIRST&page=${page}&filterArticleTypes=Research Article&unfilteredQuery=${keyword}"  # noqa: E501
        )

        super().__init__()

    def _construct_url(self, year: int, keyword: str, page: int) -> str:
        return self.search_url_template.substitute(
            keyword=keyword,
            year=year,
            page=page,
        )

    def search_all_pages(self, year: int, keyword: str) -> DataFrame:
        max_page: int = 1
        current_page: int = 1

        data: list[DataFrame] = []

        with Bar(
            f"Conducting search for {keyword} in {year}...",
            max=max_page,
        ) as bar:
            while True:
                # Break if the current page is greater than the maximum page
                if current_page > max_page:
                    break

                # Search a single page
                df: DataFrame = self.search_single_page(
                    year=year,
                    keyword=keyword,
                    page=current_page,
                )
                data.append(df)

                # If the current page is page 1, compute the max page from the responses
                if current_page == 1:
                    json: dict[str, str] = df["response_object"].pop(0).json()

                    documentsFound: int = json["searchResults"]["numFound"]

                    if documentsFound >= 100:
                        max_page: int = ceil(documentsFound / 100)
                        bar.max = max_page
                        bar.update()

                current_page += 1
                bar.next()

        return pd.concat(objs=data, ignore_index=True).drop(
            columns="response_object",
        )
