from json import dumps

from pandas import DataFrame
from pydantic import BaseModel


class MetadataModel(BaseModel):  # noqa: D101
    timestamp: float
    doi: str
    cited_by_count: int
    open_access: bool
    topic_0: str | None
    topic_1: str | None
    topic_2: str | None
    json_data: dict

    @property
    def to_df(self) -> DataFrame:  # noqa: D102
        data: dict[str, list] = {
            "timestamp": [self.timestamp],
            "doi": [self.doi],
            "cited_by_count": [self.cited_by_count],
            "open_access": [self.open_access],
            "topic_0": [self.topic_0],
            "topic_1": [self.topic_1],
            "topic_2": [self.topic_2],
            "json_data": [dumps(obj=self.json_data)],
        }

        return DataFrame(data=data)
