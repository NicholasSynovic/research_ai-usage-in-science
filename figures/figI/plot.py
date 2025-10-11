from pathlib import Path

import click
import pandas
from pandas import DataFrame


@click.command()
@click.option(
    "--flat-author-agreement",
    required=True,
    type=lambda x: Path(x).resolve(),
    help="Path to author agreement flat file in CSV format",
)
def main() -> None:
    pass


if __name__ == "__main__":
    main()
