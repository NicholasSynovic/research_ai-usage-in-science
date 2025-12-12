from json import loads
from pathlib import Path
from typing import List

import click
import pandas
from pandas import DataFrame, Series
from progress.bar import Bar
from pyfs import isFile, resolvePath


def plosExtraction(df: DataFrame) -> DataFrame:
    data: dict[str, List[str]] = {
        "journal": [],
        "query": [],
        "url": [],
    }

    baseURL: str = "https://journals.plos.org/plosone/article?id="
    with Bar("Extracting paper URLs from search results...", max=df.shape[0]) as bar:
        row: Series
        for _, row in df.iterrows():
            json: dict = loads(s=row["html"])
            searchResults: dict = json["searchResults"]
            docs: List[dict] = searchResults["docs"]

            doc: dict
            for doc in docs:
                url: str = baseURL + doc["id"]

                data["journal"].append(row["journal"])
                data["query"].append(row["query"])
                data["url"].append(url)

            bar.next()

    return DataFrame(data=data)


@click.command()
@click.option(
    "-i",
    "--input",
    "inputPath",
    type=Path,
    required=True,
    help="Path to search results Parquet file to analyze",
)
@click.option(
    "-o",
    "--output",
    "outputPath",
    type=Path,
    required=True,
    help="Path to store results in a Parquet file",
)
def main(inputPath: Path, outputPath: Path) -> None:
    absInputPath: Path = resolvePath(path=inputPath)
    absOutputPath: Path = resolvePath(path=outputPath)

    if not isFile(path=absInputPath):
        print(f"{absInputPath} is not a file")
        exit(1)

    df: DataFrame = pandas.read_parquet(
        path=absInputPath,
        columns=[
            "journal",
            "query",
            "html",
        ],
    )

    data: DataFrame
    match df["journal"][0]:
        case "PLOS":
            data = plosExtraction(df=df)
        case _:
            "Unsupported journal"
            exit(1)

    data.to_parquet(path=absOutputPath)


if __name__ == "__main__":
    main()
