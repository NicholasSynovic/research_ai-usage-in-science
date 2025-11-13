from abc import ABC, abstractmethod
from datetime import datetime, timezone
from itertools import product
from json import dumps
from logging import Logger
from string import Template

from pandas import DataFrame
from pydantic import BaseModel
from requests import Response, Session
from requests.adapters import HTTPAdapter, Retry

from aius.db import DB


class SearchModel(BaseModel):
    timestamp: float
    megajournal: str
    search_keyword: str
    year: int
    page: int
    url: str
    status_code: int
    json_data: dict


def search_model_to_df(sm: SearchModel) -> DataFrame:
    datum: dict[str, list] = {
        "timestamp": [sm.timestamp],
        "megajournal": [sm.megajournal],
        "search_keyword": [sm.search_keyword],
        "year": [sm.year],
        "page": [sm.page],
        "url": [sm.url],
        "status_code": [sm.status_code],
        "json_data": [dumps(obj=sm.json_data)],
    }

    return DataFrame(data=datum)


class ArticleModel(BaseModel):
    doi: str
    title: str
    megajournal: str
    journal: str
    search_id: int


def article_model_to_df(am: ArticleModel) -> DataFrame:
    datum: dict[str, list] = {
        "doi": [am.doi],
        "title": [am.title],
        "megajournal": [am.megajournal],
        "journal": [am.journal],
        "search_id": [am.search_id],
    }

    return DataFrame(data=datum)


class MegaJournal(ABC):
    def __init__(self) -> None:
        # Empty variables that are set by instancing classes
        self.megajournal: str = ""
        self.search_url_template: Template = Template(template="")
        self.keyword_year_products: product = product()
        self.db: DB | None = None

        # Custom HTTPS session with exponential backoff enabled
        self.session: Session = Session()
        self.session.mount(
            "https://",
            HTTPAdapter(
                max_retries=Retry(total=5, backoff_factor=1),
            ),
        )

    def search_single_page(
        self,
        logger: Logger,
        keyword_year_pair: tuple[str, int],
        page: int,
    ) -> SearchModel:
        search_url: str = self.search_url_template.substitute(
            search_keyword=keyword_year_pair[0],
            year=keyword_year_pair[1],
            page=page,
        )
        logger.info(msg=f"Searching URL: {search_url}")

        timestamp: float = datetime.now(tz=timezone.utc).timestamp()
        resp: Response = self.session.get(url=search_url)
        logger.debug(msg=f"Response status code: {resp.status_code}")
        return SearchModel(
            timestamp=timestamp,
            megajournal=self.megajournal,
            search_keyword=keyword_year_pair[0],
            status_code=resp.status_code,
            year=keyword_year_pair[1],
            page=page,
            url=search_url,
            json_data=resp.json(),
        )

    @abstractmethod
    def search(self) -> list[SearchModel]: ...

    @abstractmethod
    def parse_response(self, responses: list[SearchModel]) -> list[ArticleModel]: ...
