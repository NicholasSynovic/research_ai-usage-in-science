from abc import ABC, abstractmethod
from datetime import datetime
from itertools import product
from logging import Logger
from string import Template

from pydantic import BaseModel
from requests import Response, Session
from requests.adapters import HTTPAdapter, Retry


class SearchModel(BaseModel):
    status_code: int
    year: int
    search_keyword: str
    megajournal: str
    url: str
    json_data: dict


class ArticleModel(BaseModel):
    doi: str
    title: str
    megajournal: str
    journal: str
    search_keyword: str
    published_date: datetime
    journal_article_id: str


class MegaJournal(ABC):
    def __init__(self) -> None:
        # Empty variables that are set by instancing classes
        self.megajournal: str = ""
        self.search_url_template: Template = Template(template="")
        self.keyword_year_products: product = product()

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

        resp: Response = self.session.get(url=search_url)
        logger.debug(msg=f"Response status code: {resp.status_code}")
        return SearchModel(
            status_code=resp.status_code,
            year=keyword_year_pair[1],
            search_keyword=keyword_year_pair[0],
            megajournal=self.megajournal,
            url=search_url,
            json_data=resp.json(),
        )

    @abstractmethod
    def search(self) -> list[SearchModel]: ...

    @abstractmethod
    def parse_response(self, responses: list[SearchModel]) -> list[ArticleModel]: ...
