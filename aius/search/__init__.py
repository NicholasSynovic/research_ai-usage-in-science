from abc import ABC, abstractmethod
from typing import Iterable

import pandas
from pandas import DataFrame
from requests import Response, get

import aius


class JournalSearch(ABC):
    def __init__(self) -> None:
        self.name: str = ""

    @abstractmethod
    def _construct_url(
        self,
        year: int,
        keyword: str,
        page: int,
    ) -> str: ...

    @abstractmethod
    def search_all_pages(
        self,
        year: int,
        keyword: str,
    ) -> DataFrame: ...

    def search_single_page(self, year: int, keyword: str, page: int) -> DataFrame:
        resp: Response = get(
            url=self._construct_url(year=year, keyword=keyword, page=page),
            timeout=aius.GET_TIMEOUT,
        )

        data: dict[str, list] = {
            "year": [year],
            "keyword": [keyword],
            "page": [page],
            "url": [resp.url],
            "status_code": [resp.status_code],
            "html": [resp.content.decode(errors="ignore")],
            "journal": [self.name],
            "response_object": [resp],
        }

        return DataFrame(data=data)


def search_all_keyword_year_products(
    journal_search: JournalSearch,
    keyword_year_products: Iterable,
) -> DataFrame:
    df_list: list[DataFrame] = []

    keyword: str
    year: int
    for keyword, year in keyword_year_products:
        df_list.append(journal_search.search_all_pages(year=year, keyword=keyword))

    return pandas.concat(objs=df_list, ignore_index=True)
