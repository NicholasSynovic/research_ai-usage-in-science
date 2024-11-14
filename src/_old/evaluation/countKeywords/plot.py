from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from pandas import DataFrame

from src.utils import ifFileExistsExit

# from pandas.core.groupby.generic import DataFrameGroupBy


def plotBarValues(data: dict) -> None:
    for i, (_, value) in enumerate(zip(data.keys(), data.values())):
        plt.text(
            i,
            value + 0.25,
            str(int(value)),
            ha="center",
            color="black",
        )


def plotResults(df: DataFrame, fp: Path, outputCSV: Path) -> None:
    dfKeywords = df.drop(columns=["doi"])

    keywordSums = dfKeywords.sum().sort_values(ascending=False)
    data = keywordSums.to_dict()

    sns.barplot(x=list(data.keys()), y=list(data.values()))
    plt.title("Total Counts for Each Keyword")
    plt.xlabel("Keyword")
    plt.ylabel("Total Count")

    plotBarValues(data)

    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    plt.savefig(fp)
    plt.clf()

    keywordSums.to_csv(outputCSV, header=True)
    print(f"CSV file with keyword sums saved to {outputCSV}")

    # Identify rows where no keywords appeared
    noKeywordsDF = df[dfKeywords.sum(axis=1) == 0]

    # Save the DOIs of rows with no keywords to another CSV file
    noKeywordsDF[["doi"]].to_csv(outputCSV, index=False)
    print(f"CSV file with DOIs of rows with no keywords saved to {outputCSV}")


@click.command()
@click.option(
    "-i",
    "--input",
    "inputPath",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
    required=True,
    help="Path to search results csv file to plot data from",
)
@click.option(
    "-f",
    "--figure",
    "fig1Path",
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        readable=False,
        resolve_path=True,
        path_type=Path,
    ),
    required=True,
    help="Path to store figure 1",
)
@click.option(
    "-o",
    "--output",
    "outputPath",
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        readable=False,
        resolve_path=True,
        path_type=Path,
    ),
    required=True,
    help="Path to store output csv file",
)
def main(inputPath: Path, fig1Path: Path, outputPath: Path) -> None:
    ifFileExistsExit(fps=[fig1Path])

    print(f'Reading "{inputPath}... ')
    df: DataFrame = pandas.read_csv(inputPath)

    print("Plotting counts per keyword...")
    plotResults(df=df, fp=fig1Path, outputCSV=outputPath)


if __name__ == "__main__":
    main()
