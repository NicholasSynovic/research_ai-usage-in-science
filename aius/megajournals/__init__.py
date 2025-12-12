from abc import ABC, abstractmethod
from datetime import datetime, timezone
from itertools import product
from json import dumps
from logging import Logger
from string import Template

from pandas import DataFrame
from pydantic import BaseModel
from requests import Response, Session

from aius.db import DB
from aius.megajournals.bmj import BMJ
from aius.megajournals.f1000 import F1000
from aius.megajournals.frontiersin import FrontiersIn
from aius.megajournals.plos import PLOS
from aius.util.http_session import HTTPSession

MEGAJOURNAL_MAPPING: dict[str, object] = {
    "bmj": BMJ,
    "f1000": F1000,
    "frontiersin": FrontiersIn,
    "plos": PLOS,
}


class SearchModel(BaseModel):
    timestamp: float
    megajournal: str
    search_keyword: str
    year: int
    page: int
    url: str
    status_code: int
    json_data: dict

    @property
    def to_df(self) -> DataFrame:
        datum: dict[str, list] = {
            "timestamp": [self.timestamp],
            "megajournal": [self.megajournal],
            "search_keyword": [self.search_keyword],
            "year": [self.year],
            "page": [self.page],
            "url": [self.url],
            "status_code": [self.status_code],
            "json_data": [dumps(obj=self.json_data)],
        }

        return DataFrame(data=datum)


class ArticleModel(BaseModel):
    doi: str
    title: str
    megajournal: str
    journal: str
    search_id: int

    @property
    def to_df(self) -> DataFrame:
        datum: dict[str, list] = {
            "doi": [self.doi],
            "title": [self.title],
            "megajournal": [self.megajournal],
            "journal": [self.journal],
            "search_id": [self.search_id],
        }

        return DataFrame(data=datum)


class MegaJournal(ABC):
    def __init__(self, logger: Logger, db: DB) -> None:
        self.logger: Logger = logger
        self.db: DB = db

        # Empty variables that are set by instancing classes
        self.name: str = ""
        self.search_url_template: Template = Template(template="")
        self.keyword_year_products: product = product()

        # Custom HTTPS session with exponential backoff enabled
        session_util: HTTPSession = HTTPSession()
        self.timeout: int = session_util.timeout
        self.session: Session = session_util.session

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
        resp: Response = self.session.get(url=search_url, timeout=self.timeout)
        logger.debug(msg=f"Response status code: {resp.status_code}")

        return SearchModel(
            timestamp=timestamp,
            megajournal=self.name,
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

    @abstractmethod
    def download_jats(self, df: DataFrame, **kwargs) -> DataFrame: ...
