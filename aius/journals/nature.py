from collections import defaultdict
from json import loads
from string import Template
from typing import List

from bs4 import BeautifulSoup, ResultSet, Tag
from pandas import DataFrame
from progress.bar import Bar
from requests import Response

from src.journals._generic import Journal_ABC
from src.search import Search, SearchResultDataFrameSchema
from src.utils import formatText


class Nature(Journal_ABC):
    def __init__(self) -> None:
        self.journalName: str = "Nature"
        self.paperURLTemplate: Template = Template(
            template="https://journals.plos.org/plosone/article?id=${paperID}"
        )  # noqa: E501
        # TODO: Fix template URL
        self.searchURLTemplate: Template = Template(
            template="https://www.nature.com/search?q=${query}&order=date_desc&article_type=research&date_range=${year}-${year}&page=${page}"  # noqa: E501
        )

    def searchJournal(self, query: str, year: int) -> DataFrame:
        data: defaultdict[str, list] = defaultdict(list)
        page: int = 1
        maxPage: int = 1

        with Bar(f"Conducting search for {query} in {year}...", max=1) as bar:
            while True:
                if page > maxPage:
                    break

                url: str = self.searchURLTemplate.substitute(
                    query=query.replace(" ", "+"),
                    year=year,
                    page=page,
                )

                resp: Response = Search().search(url=url)

                data["year"].append(year)
                data["query"].append(query)
                data["page"].append(page)
                data["url"].append(url)
                data["status_code"].append(resp.status_code)
                data["html"].append(resp.content.decode(errors="ignore"))
                data["journal"].append(self.journalName)

                if page == 1:
                    htmlSoup: BeautifulSoup = BeautifulSoup(
                        markup=resp.content,
                        features="lxml",
                    )
                    nextPages: ResultSet[Tag] = htmlSoup.find_all(
                        name="li",
                        attrs={"class": "c-pagination__item"},
                    )

                    if nextPages.__len__() > 0:
                        maxPage: int = int(nextPages[-2].get(key="data-page"))
                        bar.max = maxPage
                        bar.update()

                bar.next()
                page += 1

        df: DataFrame = DataFrame(data=data)

        SearchResultDataFrameSchema(df=df)

        return df

    def extractPaperURLsFromSearchResult(self, respContent: str) -> List[str]:
        data: List[str] = []

        json: dict = loads(s=respContent)
        searchResults: dict = json["searchResults"]
        docs: List[dict] = searchResults["docs"]

        doc: dict
        for doc in docs:
            (
                data.append(
                    self.paperURLTemplate.substitute(
                        paperID=doc["id"],
                    ),
                )
            )

        return data

    def extract_DOI(self, url: str) -> str:
        splitURL: List[str] = url.split(sep="=")
        return splitURL[1]

    def extractTitleFromPaper(self, soup: BeautifulSoup) -> str:
        title: Tag = soup.find(name="h1", attrs={"id": "artTitle"})
        return formatText(string=title.text)

    def extractAbstractFromPaper(self, soup: BeautifulSoup) -> str:
        abstract: Tag = soup.find(
            name="div",
            attrs={"class": "abstract-content"},
        )
        return formatText(string=abstract.text)

    def extractContentFromPaper(self, soup: BeautifulSoup) -> str:
        content: Tag = soup.find(
            name="div",
            attrs={"id", "article-container"},
        )

        abstract: Tag = content.find(
            name="div",
            attrs={"class": "abstract-content"},
        )

        references: Tag = content.find(
            name="ol",
            attrs={"class": "reference"},
        )

        if abstract:
            abstract.decompose()

        if references:
            references.decompose()

        return formatText(string=content.text)

    def extractDataSourcesFromPaper(self, soup: BeautifulSoup) -> str:
        data: List[str] = []

        tags: ResultSet = soup.find_all(
            name="div",
            attrs={
                "class": "supplementary-material",
            },
        )

        tag: Tag
        for tag in tags:
            text: str = formatText(string=tag.text)
            data.append(text)

        return " ".join(data)

    def extractJournalTagsFromPaper(self, soup: BeautifulSoup) -> List[str]:
        data: List[str] = []

        tags: ResultSet = soup.find_all(
            name="a",
            attrs={"class": "taxo-term"},
        )

        tag: Tag
        for tag in tags:
            text: str = formatText(string=tag.text)
            data.append(f'"{self.journalName}_{text}"')

        return data
