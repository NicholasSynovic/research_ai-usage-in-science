from abc import ABC
from collections.abc import Generator
from string import Template

from bs4 import BeautifulSoup
from pandas import DataFrame, Series
from progress.bar import Bar
from requests import Response, get


class Downloader(ABC):
    def __init__(self, paper_dois: DataFrame) -> None:
        self.paper_dois = paper_dois
        self.paper_count: int = self.paper_dois.shape[0]

        # Override these in implmentation classes
        self.html_url_template: Template = Template("")
        self.jats_url_template: Template = Template("")
        self.pdf_url_template: Template = Template("")

    def create_html_urls(self) -> None:
        self.paper_dois["html_url"] = self.paper_dois["doi"].apply(
            lambda x: self.jats_url_template.substitute(
                doi_prefix_suffix=x.replace("https://doi.org/", ""),
            )
        )

    def create_jats_urls(self) -> None:
        self.paper_dois["jats_url"] = self.paper_dois["doi"].apply(
            lambda x: self.jats_url_template.substitute(
                doi_prefix_suffix=x.replace("https://doi.org/", ""),
            )
        )

    def create_pdf_urls(self) -> None:
        self.paper_dois["pdf_url"] = self.paper_dois["doi"].apply(
            lambda x: self.pdf_url_template.substitute(
                doi_prefix_suffix=x.replace("https://doi.org/", ""),
            )
        )

    def get_documents(
        self,
        column: str,
        timeout: int = 60,
    ) -> Generator[Response, None, None]:
        row: Series
        for _, row in self.paper_dois.iterrows():
            yield get(url=row[column], timeout=timeout)

    def download_html_content(self) -> None:
        data: list[str] = []

        resp: Response
        with Bar("Downloading HTML content...", max=self.paper_count) as bar:
            for resp in self.get_documents(column="html_url"):
                soup: BeautifulSoup = BeautifulSoup(
                    markup=resp.content,
                    features="lxml",
                )

                data.append(soup.prettify())
                bar.next()

        self.paper_dois["html"] = data

    def download_jats_content(self) -> None:
        data: list[str] = []

        resp: Response
        with Bar("Downloading JATS XML content...", max=self.paper_count) as bar:
            for resp in self.get_documents(column="jats_url"):
                data.append(resp.content.decode())
                bar.next()

        self.paper_dois["jats"] = data

    def download_pdf_content(self) -> None:
        data: list[bytes] = []

        resp: Response
        with Bar("Downloading PDF content...", max=self.paper_count) as bar:
            for resp in self.get_documents(column="pdf_url"):
                data.append(resp.content)
                bar.next()

        self.paper_dois["pdf"] = data


def download(journal_downloader: Downloader) -> None:
    # Create URLs
    journal_downloader.create_html_urls()
    journal_downloader.create_jats_urls()
    journal_downloader.create_pdf_urls()

    # Download content
    journal_downloader.download_html_content()
    journal_downloader.download_jats_content()
    journal_downloader.download_pdf_content()
