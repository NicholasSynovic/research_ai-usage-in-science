from aius.search import JournalSearch
from string import Template
from pandas import DataFrame
import pandas as pd
from progress.bar import Bar
from bs4 import BeautifulSoup, ResultSet, Tag


class Nature(JournalSearch):
    def __init__(self) -> None:
        # Initialize class variables
        self.name: str = "nature"

        # Create search URL template
        self.search_url_template: Template = Template(
            template="https://www.nature.com/search?q=${keyword}&order=date_desc&article_type=research&date_range=${year}-${year}&page=${page}"  # noqa: E501
        )

    def _construct_url(self, year: int, keyword: str, page: int) -> str:
        return self.search_url_template.substitute(
            keyword=keyword.replace(" ", "+"),
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
                    htmlSoup: BeautifulSoup = BeautifulSoup(
                        markup=df["response_object"].pop(0).content, features="lxml"
                    )

                    nextPages: ResultSet[Tag] = htmlSoup.find_all(
                        name="li",
                        attrs={"class": "c-pagination__item"},
                    )

                    if nextPages.__len__() > 0:
                        max_page: int = int(nextPages[-2].get(key="data-page"))
                        bar.max = max_page
                        bar.update()

                current_page += 1
                bar.next()

        return pd.concat(objs=data, ignore_index=True).drop(
            columns="response_object",
        )
