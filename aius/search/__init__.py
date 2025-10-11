from abc import ABC, abstractmethod
from typing import Iterable

import pandas
from pandas import DataFrame, Timestamp
from requests import Response, Session, get
from requests.adapters import HTTPAdapter, Retry

import aius


class JournalSearch(ABC):
    def __init__(self) -> None:
        self.name: str = ""

        # Custom HTTPS session with exponential backoff enabled
        self.session: Session = Session()
        self.session.mount(
            "https://",
            HTTPAdapter(
                max_retries=Retry(total=5, backoff_factor=1),
            ),
        )

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
        resp: Response = self.session.get(
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
            "timestamp": [Timestamp.utcnow()],
        }

        return DataFrame(data=data)


def search(
    journal_search: JournalSearch,
    keyword_year_products: Iterable,
) -> DataFrame:
    df_list: list[DataFrame] = []

    keyword: str
    year: int
    for keyword, year in keyword_year_products:
        df_list.append(
            journal_search.search_all_pages(
                year=year,
                keyword=keyword,
            )
        )

    return pandas.concat(objs=df_list, ignore_index=True)
