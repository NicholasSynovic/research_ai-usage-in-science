import sys
from itertools import product
from pathlib import Path
from typing import List

import click
import pandas
from pandas import DataFrame

from src.journals._generic import Journal_ABC
from src.journals.nature import Nature
from src.journals.plos import PLOS
from src.journals.science import Science
from src.types import SearchResultsDF
from src.utils import ifFileExistsExit

RELEVANT_YEARS: List[int] = list(range(2014, 2025))  # [2014, ..., 2025)

SEARCH_QUERIES: List[str] = [
    r'"Deep Learning"',
    r'"Deep Neural Network"',
    r'"Hugging Face"',
    r'"HuggingFace"',
    r'"Model Checkpoint"',
    r'"Model Weights"',
    r'"Pre-Trained Model"',
]


def runCollector(journal: Journal_ABC) -> DataFrame:
    data: List[DataFrame] = []

    for pair in product(SEARCH_QUERIES, RELEVANT_YEARS):
        df: DataFrame = journal.searchJournal(query=pair[0], year=pair[1])
        data.append(df)

    df: DataFrame = pandas.concat(objs=data, ignore_index=True)

    df.drop_duplicates(
        subset=["url"],
        keep="first",
        inplace=True,
        ignore_index=True,
    )

    SearchResultsDF(df_dict=df.to_dict(orient="records"))

    return df


@click.command()
@click.option(
    "-j",
    "--journal",
    "journal",
    required=False,
    type=click.Choice(
        choices=["plos", "science", "nature"], case_sensitive=False
    ),
    help="Journal to search for documents in",
    default="plos",
    show_default=True,
)
@click.option(
    "-o",
    "--output",
    "outputPath",
    required=True,
    help="Output parquet file to save Pandas DataFrame to",
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        resolve_path=True,
        path_type=Path,
    ),
)
def main(outputPath: Path, journal: str) -> None:
    ifFileExistsExit(fps=[outputPath])

    journalClass: Journal_ABC | Science
    match journal:
        case "nature":
            journalClass = Nature()
        case "plos":
            journalClass = PLOS()
        case "science":
            journalClass = Science()
            print(journalClass.message)

            journalClass.generateURLs(
                years=RELEVANT_YEARS,
                queries=SEARCH_QUERIES,
            )
            sys.exit(0)

        case _:
            sys.exit(1)

    df: DataFrame = runCollector(journal=journalClass)

    df.to_parquet(path=outputPath, engine="pyarrow")


if __name__ == "__main__":
    main()
