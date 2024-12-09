from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from pandas import DataFrame


@click.command()
@click.option(
    "-d",
    "--data",
    "dataFile",
    required=False,
    default=Path("../../data/journalTotalSearchResults.csv"),
    show_default=True,
    help="Path to CSV file containing the total number of search results per document",  # noqa: E501
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
    "outputFile",
    required=False,
    default=Path("output.pdf"),
    show_default=True,
    help="Path to save figure to",
    type=click.Path(
        exists=False,
        file_okay=True,
        writable=True,
        resolve_path=True,
        path_type=Path,
    ),
)
def main(dataFile: Path, outputFile: Path) -> None:
    df: DataFrame = pandas.read_csv(
        filepath_or_buffer=dataFile,
        index_col=None,
    )[0:3]

    sns.barplot(data=df, x="Journal", y="Count")
    plt.title(label="Number Of Search Results Per Journal")
    plt.tight_layout()
    plt.savefig(outputFile)


if __name__ == "__main__":
    main()
