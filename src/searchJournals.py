from itertools import product
from pathlib import Path
from string import Template
from typing import List

import click
import pandas
from pandas import DataFrame

from src.journals import RELEVANT_YEARS, SEARCH_QUERIES
from src.journals._generic import Journal_ABC
from src.journals.plos import PLOS
from src.utils import ifFileExistsExit

MEGA_JOURNAL_HELP_TEMPLATE: Template = Template(
    template="Search for documents in ${journal} mega journal",
)


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

    return df


@click.command()
@click.option(
    "-j",
    "--journal",
    "journal",
    required=True,
    type=click.Choice(choices=["plos"]),
    help="Search for documents in a supported mega-journal",
)
@click.option(
    "-o",
    "--output",
    "outputPath",
    required=True,
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        resolve_path=True,
        path_type=Path,
    ),
    help="Output parquet file to save Pandas DataFrame to",
)
def main(outputPath: Path, journal: str) -> None:
    ifFileExistsExit(fps=[outputPath])

    journalClass: Journal_ABC
    match journal:
        case "plos":
            journalClass = PLOS()
        case _:
            exit(1)

    df: DataFrame = runCollector(journal=journalClass)

    df.to_parquet(path=outputPath, engine="pyarrow")


if __name__ == "__main__":
    main()
