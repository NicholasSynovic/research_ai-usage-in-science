from abc import ABC, abstractmethod

from pandas import DataFrame


class JournalExtractor(ABC):
    def __init__(self) -> None:
        self.name: str = ""

    @abstractmethod
    def extract_all_papers(self, search_data: DataFrame) -> DataFrame: ...
