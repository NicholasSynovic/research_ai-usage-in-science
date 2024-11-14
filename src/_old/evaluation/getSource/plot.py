from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas
import seaborn as sns


def plotBarValues(data: dict) -> None:
    for i, (_, value) in enumerate(zip(data.keys(), data.values())):
        plt.text(
            i,
            value + 0.25,
            str(int(value)),
            ha="center",
            color="black",
        )


def plot(input: str, output: str) -> None:
    df = pandas.read_csv(input)

    if "Domain" not in df.columns:
        raise ValueError("The CSV file must contain a 'Domain' column.")

    domainCounts = df["Domain"].value_counts()

    topDomains = domainCounts.head(10).reset_index()
    topDomains.columns = ["Domain", "Count"]

    plt.figure(figsize=(12, 8))

    sns.barplot(
        x="Domain",
        y="Count",
        data=topDomains,
        palette="viridis",
        hue="Domain",
        dodge=False,
    )

    plt.xlabel("Domain")
    plt.ylabel("Frequency")

    plotBarValues(topDomains.set_index("Domain")["Count"].to_dict())

    plt.title("Top 10 Most Occurring Domains of Paper Artifact Locations")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output)
    plt.show()


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
    help="Path to a csv file of domains",
)
@click.option(
    "-o",
    "--output",
    "outputPath",
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
    help="Path to a png file of plots",
)
def main(inputPath: Path, outputPath: Path) -> None:
    plot(inputPath, outputPath)


if __name__ == "__main__":
    main()
