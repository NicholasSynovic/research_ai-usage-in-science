from abc import ABC, abstractmethod
from requests import Response, get
from pandas import DataFrame


GET_TIMEOUT: int = 60


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
            timeout=GET_TIMEOUT,
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
