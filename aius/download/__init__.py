from abc import ABC, abstractmethod
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

    def get_documents(
        self,
        column: str,
        timeout: int = 60,
    ) -> Generator[Response, None, None]:
        row: Series
        for _, row in self.paper_dois.iterrows():
            yield get(url=row[column], timeout=timeout)


def download(df: DataFrame, journal_downloader: Downloader) -> DataFrame:
    # Create URLs
    journal_downloader.create_html_urls()
    journal_downloader.create_jats_urls()
    journal_downloader.create_pdf_urls()

    # Download

    return journal_downloader.paper_dois


# class Downloader:
#     def __init__(self, data: DataFrame, pdf_dir: Path) -> None:
#         self.data: DataFrame = data
#         self.pdf_dir: Path = pdf_dir

#     def _get_plos(self, doi: str) -> Response:
#         # Get DOI prefix/suffix from DOI
#         doi_prefix_suffix: str = doi.replace("https://doi.org/", "")

#         # Create PLOS PDF URL
#         url: str = f"https://journals.plos.org/plosone/article/file?id={doi_prefix_suffix}&type=printable"

#         # Return the response
#         return get(url=url, timeout=aius.GET_TIMEOUT)

#     def _get_nature(self, doi: str) -> Response:
#         # Get DOI suffix from DOI
#         doi_suffix: str = doi.split(sep="/")[-1]

#         # Create Nature PDF URL
#         url: str = f"https://www.nature.com/articles/{doi_suffix}.pdf"

#         # Return the response
#         return get(url=url, timeout=aius.GET_TIMEOUT)

#     def download(self) -> None:
#         with Bar("Downloading data...", max=self.data.shape[0]) as bar:
#             row: Series
#             for _, row in self.data.iterrows():
#                 # Create filename from doi prefix and suffix
#                 filename: str = f"{row['doi'].replace('https://doi.org/', '').replace('/', '_')}.pdf"

#                 # Create filepath for PDF
#                 filepath: Path = Path(self.pdf_dir, filename)

#                 # Check if file exists at that filepath and skip processing it
#                 if filepath.exists():
#                     bar.next()
#                     continue

#                 # Get PDF response
#                 resp: Response
#                 match row["journal"]:
#                     case "nature":
#                         resp = self._get_nature(doi=row["doi"])
#                     case "plos":
#                         resp = self._get_plos(doi=row["doi"])
#                     case _:
#                         raise TypeError("Not a valid journal")

#                 # Write data from the response
#                 filepath.write_bytes(data=resp.content)

#                 bar.next()
