import click
from pandas import DataFrame
import pandas
from pathlib import Path

@click.command()
@click.option(
    "--flat-author-agreement",
    required=True,
    type=lambda x: Path(x).resolve(),
    help="Path to author agreement flat file in CSV format"
)
def main()  ->  None:
    pass

if __name__ == '__main__':
    main()
