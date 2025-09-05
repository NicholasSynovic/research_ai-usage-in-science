from pathlib import Path

import click
import pandas
from pandas import DataFrame
from pyfs import resolvePath

from aius.classes.plos import PLOS


@click.command()
@click.option(
    "-i",
    "--input",
    "inputPath",
    type=Path,
    required=True,
    help="Path to downloaded list of academic papers",
)
def main(inputPath: Path) -> None:
    absInputPath: Path = resolvePath(path=inputPath)

    plos: PLOS = PLOS()

    df: DataFrame = pandas.read_parquet(
        path=absInputPath,
        engine="pyarrow",
    )

    df["doi"] = df["url"].apply(
        lambda x: f"https://doi.org/{plos.extractDOIFromPaper(url=x)}",
    )

    df.to_parquet(path=absInputPath.with_suffix(".new.parquet"))


if __name__ == "__main__":
    main()
