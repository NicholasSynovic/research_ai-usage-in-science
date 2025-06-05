from pathlib import Path
from typing import List

import click
import pandas
from pandas import DataFrame, Timestamp
from pandas.core.groupby.generic import DataFrameGroupBy

from src.utils import ifFileExistsExit


def groupByYear(df: DataFrame) -> DataFrameGroupBy:
    df["year"] = df["publication_date"].apply(
        lambda x: Timestamp(ts_input=x).year
    )
    return df.groupby(by="year")


def sampleDFs(dfgb: DataFrameGroupBy) -> DataFrame:
    data: List[DataFrame] = []

    df: DataFrame
    for _, df in dfgb:
        sampledDF: DataFrame = df.sample(
            n=10,
            replace=False,
            random_state=42,
            ignore_index=True,
        )

        data.append(sampledDF)

    return pandas.concat(objs=data, ignore_index=True)


@click.command()
@click.option(
    "-i",
    "--input",
    "inputPath",
    required=True,
    help="Natrual Science documents results in Apache Parquet format",
    type=click.Path(
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
)
@click.option(
    "-o",
    "--output",
    "outputPath",
    required=True,
    help="Apache Parquet file to write sampled Natrual Science documents",
    type=click.Path(
        exists=False,
        file_okay=True,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
)
def main(inputPath: Path, outputPath: Path) -> None:
    """
    Given the metadata of documents from a journal, output a Pandas DataFrame that of documents that are categorized as Natural Sciences by OpenAlex as a as an Apache Parquet file.

    Only documents that have an OpenAlex listing, are cited at least once, and have two or more topics assigned by OpenAlex are considered in the filtering process.

    These documents are meant to be post-processed for usage in other scripts.

    While the data outputted from this script can be leveraged independently, it is better to use this data in the following pipeline:

    aius-search-journal -> aius-extract-documents -> **aius-filter-documents** -> aius-sample-documents -> aius-download-documents
    """  # noqa: E501
    ifFileExistsExit(fps=[outputPath])

    df: DataFrame = pandas.read_parquet(path=inputPath, engine="pyarrow")

    dfgb: DataFrameGroupBy = groupByYear(df=df)

    sampledDF: DataFrame = sampleDFs(dfgb=dfgb)

    sampledDF.to_parquet(path=outputPath, engine="pyarrow")


if __name__ == "__main__":
    main()
