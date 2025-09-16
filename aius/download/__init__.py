from abc import ABC, abstractmethod
from pathlib import Path

from pandas import DataFrame, Series
from progress.bar import Bar
from requests import Response, get

import aius


class Downloader(ABC):
    def __init__(self, paper_dois: DataFrame) -> None:
        self.paper_dois = paper_dois

    def _get(self, url: str, timeout: int = 60) -> Response:
        return get(url=url, timeout=timeout)

    @abstractmethod
    def create_pdf_urls(self) -> None:
        """
        Modifies self.paper_dois in place to add a new column `pdf_urls`.

        This column contains links to the PDF content of paper DOIs.
        """
        ...

    @abstractmethod
    def create_html_urls(self) -> None:
        """
        Modifies self.paper_dois in place to add a new column `html_urls`.

        This column contains links to the HTML content of paper DOIs.
        """
        ...

    @abstractmethod
    def get_pdfs(self) -> Response:
        """Yield PDF URL `requests.Response` objects"""
        ...

    @abstractmethod
    def get_html(self) -> Response:
        """Yield HTML URL `requests.Response` objects"""
        ...


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
