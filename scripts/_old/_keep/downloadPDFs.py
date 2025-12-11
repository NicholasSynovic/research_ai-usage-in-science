import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from string import Template
from typing import List
from urllib.parse import urlparse

import click
import pandas
from pandas import DataFrame
from progress.bar import Bar
from requests import Response, get

from aius.db.db import DB

URL_SOURCE: str = "PLOS"


def getResponse(doi: str) -> Response:
    host: str = "journals.plos.org"
    urlTemplate: Template = Template(
        template="https://journals.plos.org/plosone/article/file?id=${doi}&type=printable"  # noqa: E501
    )

    url: str = urlTemplate.substitute(doi=doi)

    return get(url=url, timeout=60, headers={"Host": host})


def url2doi(url: str) -> str:
    query: str = urlparse(url=url).query
    return query[3::].split("&")[0].replace("/", "_")


def savePDF(response: Response, outputDir: Path) -> None:
    url: str = response.url
    doi: str = url2doi(url=url)

    fp: Path = Path(outputDir, doi + ".pdf")

    with open(file=fp, mode="wb") as pdf:
        pdf.write(response.content)
        pdf.close()


@click.command()
@click.option(
    "-i",
    "--input",
    "inputDB",
    help="Path to db",
    type=click.Path(
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
    required=True,
)
@click.option(
    "-o",
    "--output-dir",
    "outputDir",
    help="Path to write files",
    type=click.Path(
        exists=True,
        dir_okay=True,
        writable=True,
        resolve_path=True,
        path_type=Path,
    ),
    required=True,
)
@click.option(
    "-t",
    "--type",
    "documentType",
    help="Type of document to download",
    type=click.Choice(
        choices=["author-agreement", "plos", "nature"],
        case_sensitive=True,
    ),
    default="author-agreement",
    show_default=True,
    required=False,
)
def main(inputDB: Path, outputDir: Path, documentType: str) -> None:
    responses: List[Response] = []

    db: DB = DB(fp=inputDB)

    df: DataFrame = DataFrame()
    if documentType == "author-agreement":
        sql: str = "SELECT T1.doi FROM documents AS T1 INNER JOIN author_agreement AS T2 ON T2.document_id = T1.id;"  # noqa: E501
        df = pandas.read_sql_query(sql=sql, con=db.engine)
    else:
        sys.exit(1)

    dois: List[str] = df["doi"].to_list()

    with Bar("Downloading pdfs...", max=len(dois)) as bar:
        with ThreadPoolExecutor() as executor:

            def _run(doi: str) -> None:
                responses.append(getResponse(doi))
                bar.next()

            executor.map(_run, dois)

    with Bar("Saving PDFs to disk...", max=len(responses)) as bar:
        resp: Response
        for resp in responses:
            if resp.status_code == 200:
                savePDF(response=resp, outputDir=outputDir)

            else:
                with open(
                    file=Path(outputDir, documentType + "_errors.txt"),
                    mode="a",
                ) as err:
                    err.write(f"{resp.status_code} {url2doi(resp.url)}")
                    err.close()

            bar.next()


if __name__ == "__main__":
    main()
