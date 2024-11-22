from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from pandas import DataFrame

from src.utils import ifFileExistsExit


def plotBarValues(data: dict) -> None:
    for i, (_, value) in enumerate(zip(data.keys(), data.values())):
        plt.text(
            i,
            value + 0.25,
            str(int(value)),
            ha="center",
            color="black",
        )


def plotResults(df: DataFrame, fp: Path) -> None:

    df["tags"] = df["tags"].str.replace("PLOS_", "", regex=False)
    dfSorted = df.sort_values(by="count", ascending=False).head(10)

    sns.barplot(x="tags", y="count", data=dfSorted)
    plt.title("Top 10 Tags by Count")
    plt.xlabel("OpenAlex Tag")
    plt.ylabel("Count")

    plotBarValues(dfSorted.set_index("tags")["count"].to_dict())

    plt.xticks(rotation=50, ha="right")

    plt.tight_layout()
    plt.show()
    plt.savefig(fp)
    plt.clf()


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
def main(inputPath: Path, fig1Path: Path) -> None:
    ifFileExistsExit(fps=[fig1Path])

    print(f'Reading "{inputPath}... ')
    df: DataFrame = pandas.read_csv(inputPath)

    print("Plotting count per tag...")
    plotResults(df=df, fp=fig1Path)


if __name__ == "__main__":
    main()
