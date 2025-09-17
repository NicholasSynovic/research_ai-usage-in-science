from abc import ABC, abstractmethod
from collections.abc import Generator

from pandas import DataFrame, Series
from requests import Response, get


class Downloader(ABC):
    def __init__(self, paper_dois: DataFrame) -> None:
        self.paper_dois = paper_dois
        self.paper_count: int = self.paper_dois.shape[0]

    @abstractmethod
    def create_html_urls(self) -> None:
        """
        Modifies self.paper_dois in place to add a new column `html_urls`.

        This column contains links to the PDF content of paper DOIs.
        """
        ...

    @abstractmethod
    def create_jats_urls(self) -> None:
        """
        Modifies self.paper_dois in place to add a new column `jats_urls`.

        This column contains links to the JATS XML content of paper DOIs.
        """
        ...

    @abstractmethod
    def create_pdf_urls(self) -> None:
        """
        Modifies self.paper_dois in place to add a new column `pdf_urls`.

        This column contains links to the PDF content of paper DOIs.
        """
        ...

    @abstractmethod
    def extract_html_content(self) -> None: ...

    @abstractmethod
    def extract_jats_content(self) -> None: ...

    @abstractmethod
    def extract_pdf_content(self) -> None: ...

    def get_documents(
        self,
        column: str,
        timeout: int = 60,
    ) -> Generator[Response, None, None]:
        row: Series
        for _, row in self.paper_dois.iterrows():
            yield get(url=row[column], timeout=timeout)


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
