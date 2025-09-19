from abc import ABC, abstractmethod
from collections.abc import Generator
from pathlib import Path
from string import Template

from bs4 import BeautifulSoup
from pandas import DataFrame, Series
from progress.bar import Bar
from requests import Response, get
from requests.exceptions import HTTPError


class Downloader(ABC):
    def __init__(self, paper_dois: DataFrame, output_dir: Path) -> None:
        self.paper_dois = paper_dois.copy()
        self.paper_count: int = self.paper_dois.shape[0]

        # Output directory
        self.output_dir: Path = output_dir

    @abstractmethod
    def create_html_urls(self) -> None: ...

    @abstractmethod
    def create_jats_urls(self) -> None: ...

    @abstractmethod
    def create_pdf_urls(self) -> None: ...

    def get_documents(
        self,
        column: str,
        timeout: int = 60,
    ) -> Generator[Response, None, None]:
        row: Series
        for _, row in self.paper_dois.iterrows():
            if (
                Path(self.output_dir, f"{row['ns_paper_id']}.{column.split('_')[0]}")
                .absolute()
                .exists()
            ):
                continue
            else:
                yield get(url=row[column], timeout=timeout)

    def download_html_content(self) -> None:
        data: list[str] = []

        resp: Response
        with Bar("Downloading HTML content...", max=self.paper_count) as bar:
            for resp in self.get_documents(column="html_url"):
                if resp.status_code != 200:
                    raise HTTPError(
                        f"{resp.status_code, resp.url, resp.reason}",
                        response=resp,
                    )

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
                if resp.status_code != 200:
                    raise HTTPError(
                        f"{resp.status_code, resp.url, resp.reason}",
                        response=resp,
                    )

                soup: BeautifulSoup = BeautifulSoup(
                    markup=resp.content,
                    features="lxml-xml",
                )

                data.append(soup.prettify())
                bar.next()

        self.paper_dois["jats"] = data

    def download_pdf_content(self) -> None:
        data: list[bytes] = []

        resp: Response
        with Bar("Downloading PDF content...", max=self.paper_count) as bar:
            for resp in self.get_documents(column="pdf_url"):
                if resp.status_code != 200:
                    raise HTTPError(
                        f"{resp.status_code, resp.url, resp.reason}",
                        response=resp,
                    )

                data.append(resp.content)
                bar.next()

        self.paper_dois["pdf"] = data


def download_and_write_to_fs_content(journal_downloader: Downloader) -> None:
    # Create URLs
    journal_downloader.create_html_urls()
    journal_downloader.create_jats_urls()
    journal_downloader.create_pdf_urls()

    # Download HTML content
    journal_downloader.download_html_content()
    for _, row in journal_downloader.paper_dois.iterrows():
        fp: Path = Path(journal_downloader.output_dir, f"{row['ns_paper_id']}.html")
        fp.write_text(data=row["html"])

    # Download JATS content
    journal_downloader.download_jats_content()
    for _, row in journal_downloader.paper_dois.iterrows():
        fp: Path = Path(journal_downloader.output_dir, f"{row['ns_paper_id']}.jats.xml")
        fp.write_text(data=row["jats"])

    # Download PDF content
    journal_downloader.download_pdf_content()
    for _, row in journal_downloader.paper_dois.iterrows():
        fp: Path = Path(journal_downloader.output_dir, f"{row['ns_paper_id']}.pdf")
        fp.write_text(data=row["pdf"])
