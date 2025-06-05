from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from string import Template
from typing import List
from urllib.parse import urlparse

from progress.bar import Bar
from requests import Response, get

from aius.db import DB


def _getResponse(doi: str) -> Response:
    host: str = "journals.plos.org"
    urlTemplate: Template = Template(
        template="https://journals.plos.org/plosone/article/file?id=${doi}&type=printable"  # noqa: E501
    )

    url: str = urlTemplate.substitute(doi=doi)

    return get(url=url, timeout=60, headers={"Host": host})


def __url2doi(url: str) -> str:
    query: str = urlparse(url=url).query
    return query[3::].split("&")[0].replace("/", "_")


def _savePDF(response: Response, outputDir: Path) -> None:
    url: str = response.url
    doi: str = __url2doi(url=url)

    fp: Path = Path(outputDir, doi + ".pdf")

    with open(file=fp, mode="wb") as pdf:
        pdf.write(response.content)
        pdf.close()


def downloadPLOSPDFs(dois: List[str], outputDir: Path) -> None:
    responses: List[Response] = []

    with Bar("Downloading pdfs...", max=len(dois)) as bar:
        with ThreadPoolExecutor() as executor:

            def _run(doi: str) -> None:
                responses.append(_getResponse(doi))
                bar.next()

            executor.map(_run, dois)

    with Bar("Saving PDFs to disk...", max=len(responses)) as bar:
        resp: Response
        for resp in responses:
            if resp.status_code == 200:
                _savePDF(response=resp, outputDir=outputDir)

            else:
                with open(file=Path(outputDir, "errors.txt"), mode="a") as err:
                    err.write(
                        f"{resp.status_code} {__url2doi(resp.url)} {resp.url}",
                    )
                    err.close()

            bar.next()


def download(dbFP: Path, sample: str, outputDir: Path) -> None | int:
    db: DB = DB(fp=dbFP)

    dois: List[str] = []
    match sample:
        case "author-agreement":
            dois = db.getAuthorAgreementDOIs()["doi"].to_list()
        case "plos-ns":
            dois = db.get_PLOS_OA_NS_PaperDOIs()["doi"].to_list()
        case _:
            return 0

    downloadPLOSPDFs(dois=dois, outputDir=outputDir)
