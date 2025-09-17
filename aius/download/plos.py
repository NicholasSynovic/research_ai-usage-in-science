from string import Template

from bs4 import BeautifulSoup
from pandas import DataFrame
from progress.bar import Bar
from requests import Response

from aius.download import Downloader


class PLOS(Downloader):
    def __init__(self, paper_dois: DataFrame) -> None:
        super().__init__(paper_dois)

        self.html_url_template: Template = Template(
            template="https://journals.plos.org/plosone/article/file?id=${doi_prefix_suffix}"
        )
        self.jats_url_template: Template = Template(
            template="https://journals.plos.org/plosone/article/file?id=${doi_prefix_suffix}&type=manuscript"
        )
        self.pdf_url_template: Template = Template(
            template="https://journals.plos.org/plosone/article/file?id=${doi_prefix_suffix}&type=printable"
        )

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

    def extract_html_content(self) -> None:
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

        self.paper_dois["raw_html_content"] = data

    def extract_jats_content(self) -> None:
        data: list[str] = []

        resp: Response
        with Bar("Downloading JATS XML content...", max=self.paper_count) as bar:
            for resp in self.get_documents(column="html_url"):
                data.append(resp.content.decode())
                bar.next()

        self.paper_dois["raw_jats_content"] = data

    def extract_pdf_content(self) -> None:
        data: list[bytes] = []

        resp: Response
        with Bar("Downloading PDF content...", max=self.paper_count) as bar:
            for resp in self.get_documents(column="html_url"):
                data.append(resp.content)
                bar.next()

        self.paper_dois["raw_pdf_content"] = data
