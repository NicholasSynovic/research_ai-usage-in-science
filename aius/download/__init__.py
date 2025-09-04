from pathlib import Path

from pandas import DataFrame, Series
from progress.bar import Bar
from requests import Response, get

import aius


class Downloader:
    def __init__(self, data: DataFrame, pdf_dir: Path) -> None:
        self.data: DataFrame = data
        self.pdf_dir: Path = pdf_dir

    def _get_plos(self, doi: str) -> Response:
        # Get DOI prefix/suffix from DOI
        doi_prefix_suffix: str = doi.replace("https://doi.org/", "")

        # Create PLOS PDF URL
        url: str = f"https://journals.plos.org/plosone/article/file?id={doi_prefix_suffix}&type=printable"

        # Return the response
        return get(url=url, timeout=aius.GET_TIMEOUT)

    def _get_nature(self, doi: str) -> Response:
        # Get DOI suffix from DOI
        doi_suffix: str = doi.split(sep="/")[-1]

        # Create Nature PDF URL
        url: str = f"https://www.nature.com/articles/{doi_suffix}.pdf"

        # Return the response
        return get(url=url, timeout=aius.GET_TIMEOUT)

    def _write_pdf(self, resp: Response, doi: str) -> None:
        # Create filename from doi prefix and suffix
        filename: str = f"{doi.replace('https://doi.org/', '').replace('/', '_')}.pdf"

        # Create filepath
        filepath: Path = Path(self.pdf_dir, filename)

        # Write data from the resp
        filepath.write_bytes(data=resp.content)

    def download(self) -> None:
        with Bar("Downloading data...", max=self.data.shape[0]) as bar:
            row: Series
            for _, row in self.data.iterrows():
                resp: Response
                match row["journal"]:
                    case "nature":
                        resp = self._get_nature(doi=row["doi"])
                    case "plos":
                        resp = self._get_plos(doi=row["doi"])
                    case _:
                        raise TypeError("Not a valid journal")

                self._write_pdf(resp=resp, doi=row["doi"])
                bar.next()
