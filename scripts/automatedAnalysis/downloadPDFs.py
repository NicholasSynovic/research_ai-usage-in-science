from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from string import Template
from typing import List
from urllib.parse import urlparse

import click
import pandas
from pandas import DataFrame, Index
from progress.bar import Bar
from requests import Response, get
from sqlalchemy import Engine, create_engine


def getDOIs(dbPath: Path) -> List[str]:
    dbEngine: Engine = create_engine(url=f"sqlite:///{dbPath}")

    searchResponsesDF: DataFrame = pandas.read_sql_table(
        table_name="search_responses",
        con=dbEngine,
        index_col="id",
    )
    plosResponsesDF: DataFrame = searchResponsesDF[
        searchResponsesDF["journal"] == 1
    ]
    plosIndex: Index = plosResponsesDF.index

    searchResultsDF: DataFrame = pandas.read_sql_table(
        table_name="search_results",
        con=dbEngine,
        index_col="id",
    )
    plosResultsDF: DataFrame = searchResultsDF[
        searchResultsDF["response_id"].isin(plosIndex)
    ]

    documentsDF: DataFrame = pandas.read_sql_table(
        table_name="documents",
        con=dbEngine,
    )
    plosDocuments: DataFrame = documentsDF[
        documentsDF["id"].isin(plosResultsDF["document_id"])
    ]

    return plosDocuments["doi"].to_list()


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
    "inputFP",
    help="Path to input PDF file",
    required=True,
    type=click.Path(
        exists=True,
        file_okay=True,
        resolve_path=True,
        path_type=Path,
    ),
)
@click.option(
    "-o",
    "--output",
    "outputDir",
    help="Path to store PDF files",
    required=True,
    type=click.Path(
        exists=True,
        dir_okay=True,
        resolve_path=True,
        path_type=Path,
    ),
)
def main(inputFP: Path, outputDir: Path) -> None:
    responses: List[Response] = []

    dois: List[str] = getDOIs(dbPath=inputFP)

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
                with open(file=Path(outputDir, "errors.txt"), mode="a") as err:
                    err.write(f"{resp.status_code} {url2doi(resp.url)}")
                    err.close()

            bar.next()


if __name__ == "__main__":
    main()
