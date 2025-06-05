from abc import ABCMeta, abstractmethod
from typing import List

from bs4 import BeautifulSoup
from pandas import DataFrame


class Journal_ABC(metaclass=ABCMeta):
    @abstractmethod
    def searchJournal(self, query: str, year: int) -> DataFrame:
        pass

    @abstractmethod
    def extractPaperURLsFromSearchResult(self, respContent: str) -> List[str]:
        pass

    @abstractmethod
    def extract_DOI(self, url: str) -> str:
        pass

    @abstractmethod
    def extractTitleFromPaper(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def extractAbstractFromPaper(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def extractContentFromPaper(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def extractDataSourcesFromPaper(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def extractJournalTagsFromPaper(self, soup: BeautifulSoup) -> List[str]:
        pass
