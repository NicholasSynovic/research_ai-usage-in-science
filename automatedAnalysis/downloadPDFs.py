from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from string import Template
from typing import List

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
        template="https://journals.plos.org/plosone/article/file?id=${doi}&type=printable"
    )

    url: str = urlTemplate.substitute(doi=doi)

    return get(url=url, timeout=60, headers={"Host": host})


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

            executor.map(_run, dois[0:100])

    print(responses)


if __name__ == "__main__":
    main()
