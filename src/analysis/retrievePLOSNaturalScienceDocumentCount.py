from pathlib import Path

import click
import pandas
from pandas import DataFrame


@click.command()
@click.option(
    "-d",
    "--documents",
    "documents",
    help="Path to PLOS documents (post Natural Science filtering)",
    required=True,
    type=click.Path(
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
)
def main(documents: Path) -> None:
    df: DataFrame = pandas.read_parquet(path=documents, engine="pyarrow")
    print("Number of filtered documents:", df.shape[0])


if __name__ == "__main__":
    main()
