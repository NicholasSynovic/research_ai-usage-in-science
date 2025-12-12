from json import dumps

from pandas import DataFrame
from pydantic import BaseModel


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
