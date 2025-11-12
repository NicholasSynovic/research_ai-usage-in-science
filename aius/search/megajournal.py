from abc import ABC, abstractmethod
from datetime import datetime
from itertools import product
from string import Template

from pydantic import BaseModel
from requests import Response, Session
from requests.adapters import HTTPAdapter, Retry


class ResponseModel(BaseModel):
    response: dict
    status_code: int
    year: int
    search_keyword: str
    megajournal: str
    url: str


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

    @abstractmethod
    def search(self) -> list[ResponseModel]: ...

    @abstractmethod
    def parse_response(self, responses: list[ResponseModel]) -> list[ArticleModel]: ...
