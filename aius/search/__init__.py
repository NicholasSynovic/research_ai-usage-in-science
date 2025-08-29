from abc import ABC, abstractmethod
from requests import Response, get

GET_TIMEOUT: int = 60

SEARCH_RESULTS: dict[str, list] = {
    "year": [],
    "query": [],
    "page": [],
    "url": [],
    "status_code": [],
    "html": [],
    "journal": [],
}


class JournalSearch(ABC):
    def __init__(self) -> None:
        pass

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
    ) -> list[Response]: ...

    def search_single_page(self, year: int, keyword: str, page: int) -> Response:
        return get(
            url=self._construct_url(year=year, keyword=keyword, page=page),
            timeout=GET_TIMEOUT,
        )
