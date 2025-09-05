from pathlib import Path
from pprint import pprint as print
from typing import List

import click
import matplotlib.pyplot as plt
import pandas
import seaborn as sns  # Import seaborn explicitly
from numpy import ndarray
from pandas import DataFrame


def plotOATagCounts(data: dict[str, List[str | int]], fp: Path) -> None:
    # Use the correct function to create a barplot
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(x="category", y="value", data=data, ax=ax)

    # Add title and labels
    ax.set_title("Number of OA Unique Topics, Subfields, Fields, and Domains")
    ax.set_xlabel("Category")
    ax.set_ylabel("Count")

    # Rotate x-axis labels for better readability
    ax.tick_params(axis="x", labelrotation=45)

    # Add value to each bar
    for p in range(len(data["category"])):
        val = data["value"][p]
        ax.text(p, val, str(val), ha="center", va="bottom")

    plt.tight_layout()
    plt.savefig(fp)

    plt.close()


@click.command()
@click.option(
    "-i",
    "--input",
    "inputPath",
    type=Path,
    required=True,
    help="Path to OpenAlex topic mapping table (CSV)",
)
@click.option(
    "-o",
    "--output",
    "outputPath",
    type=Path,
    required=True,
    help="Path to save figure (PNG)",
)
def main(inputPath: Path, outputPath: Path) -> None:
    df: DataFrame = pandas.read_csv(filepath_or_buffer=inputPath)

    uniqueTopics: ndarray = df["topic_name"].unique()
    uniqueSubfields: ndarray = df["subfield_name"].unique()
    uniqueFields: ndarray = df["field_name"].unique()
    uniqueDomains: ndarray = df["domain_name"].unique()

    data: dict[str, List[str | int]] = {
        "category": ["Topics", "Subfields", "Fields", "Domains"],
        "value": [
            uniqueTopics.size,
            uniqueSubfields.size,
            uniqueFields.size,
            uniqueDomains.size,
        ],
    }

    plotOATagCounts(data=data, fp=outputPath)

    print(uniqueFields.tolist())


if __name__ == "__main__":
    main()
