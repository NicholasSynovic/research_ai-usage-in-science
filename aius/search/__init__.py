from typing import List, Type

from requests import Response, get
from requests.exceptions import ReadTimeout
from typedframe import TypedDataFrame

SEARCH_RESULTS_STOR: dict[str, List[str | int | bytes]] = {
    "year": [],
    "query": [],
    "page": [],
    "url": [],
    "status_code": [],
    "html": [],
    "journal": [],
}


class SearchResultDataFrameSchema(TypedDataFrame):
    schema: dict[str, Type] = {
        "year": int,
        "query": str,
        "page": int,
        "url": str,
        "status_code": int,
        "html": str,
        "journal": str,
    }


class Search:
    def __init__(
        self,
        headers: dict[str, str] = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",  # noqa: E501,
        },
    ) -> None:
        self.headers: dict[str, str] = headers

    def search(self, url: str) -> Response | None:
        try:
            resp: Response = get(
                url=url,
                headers=self.headers,
                timeout=60,
                allow_redirects=True,
            )
        except ReadTimeout:
            return None
        return resp
