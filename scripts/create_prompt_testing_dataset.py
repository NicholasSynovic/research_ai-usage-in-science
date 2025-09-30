from pathlib import Path

import click
import pandas
from pandas import DataFrame

DOIS: list[str] = [
    "journal.pcbi.1010512.xml",
    "journal.pcbi.1011818.xml",
    "journal.pdig.0000536.xml",
    "journal.pgen.1009436.xml",
    "journal.pntd.0010937.xml",
    "journal.pone.0086152.xml",
    "journal.pone.0088597.xml",
    "journal.pone.0093666.xml",
    "journal.pone.0095718.xml",
    "journal.pone.0096811.xml",
    "journal.pone.0101765.xml",
    "journal.pone.0103831.xml",
    "journal.pone.0113159.xml",
    "journal.pone.0114812.xml",
    "journal.pone.0120570.xml",
    "journal.pone.0185844.xml",
    "journal.pone.0192011.xml",
    "journal.pone.0196302.xml",
    "journal.pone.0209649.xml",
    "journal.pone.0217305.xml",
]


def load_parquet(fp: Path) -> DataFrame:
    # Read file contents from Apache Parquet file
    return pandas.read_parquet(path=fp, engine="pyarrow")


@click.command()
@click.option(
    "-i",
    "--input-path",
    help="Path to formatted Markdown Apache Parquet file",
    type=lambda x: Path(x).resolve(),
)
@click.option(
    "-o",
    "--output-path",
    help="Path to write Apache Parquet file to",
    type=lambda x: Path(x).resolve(),
)
def main(input_path: Path, output_path: Path) -> None:
    df: DataFrame = load_parquet(fp=input_path)
    df = df[df["filename"].isin(values=DOIS)]
    df.to_parquet(path=output_path, engine="pyarrow")


if __name__ == "__main__":
    main()
