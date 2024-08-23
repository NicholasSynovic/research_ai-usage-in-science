from pathlib import Path
from webbrowser import open_new_tab

import click
import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from pandas import DataFrame, Series


def plotBarValues(data: dict) -> None:
    for i, (_, value) in enumerate(zip(data.keys(), data.values())):
        plt.text(
            i,
            value + 0.05,
            str(int(value)),
            ha="center",
            color="black",
        )


def plotFieldCount(df: DataFrame, fp: str) -> None:
    data: Series = df["field"].explode()
    data = data.str.replace(pat=" and", repl="\nand")
    data = data.str.replace(
        pat="Physics\nand Astronomy",
        repl="Physics and\nAstronomy",
    )
    data = data.value_counts(sort=True, ascending=False)

    sns.barplot(data=data)
    plt.title(
        label="Number Of Natural Science Papers By OpenAlex Topic",
        fontsize="x-large",
    )
    plt.xlabel(xlabel="OA Topic Label", labelpad=10, fontsize="large")
    plt.ylabel(ylabel="Count", fontsize="large")
    plt.xticks(rotation=45, ha="right")

    plotBarValues(data=data.to_dict())

    plt.tight_layout()
    plt.savefig(fp)
    plt.clf()


@click.command()
@click.option(
    "-i",
    "--input",
    "inputPath",
    required=True,
    help="Path to PLOS filtered samples",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
)
def main(inputPath: Path) -> None:
    df: DataFrame = pandas.read_json(path_or_buf=inputPath)

    relevantPapers: DataFrame = df[df["ns"] == True]  # noqa: E712

    doi: DataFrame
    for doi in relevantPapers["doi"]:  # noqa: E712
        open_new_tab(url=doi)

    plotFieldCount(df=relevantPapers, fp="numberOfNSPapersByOATopic.png")


if __name__ == "__main__":
    main()