from pathlib import Path
from urllib.parse import urlparse

import click
import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from pandas import DataFrame


def plotBarValues(data: dict) -> None:
    for i, (_, value) in enumerate(zip(data.keys(), data.values())):
        plt.text(
            i,
            value + 0.25,
            str(int(value)),
            ha="center",
            color="black",
        )


def extract_domain(url: str):
    print(f"Processing URL: {url}")

    if pandas.notna(url):
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc

        # Remove any port number
        domain = netloc.split(":")[0]

        parts = domain.split(".")
        if len(parts) >= 2:
            return ".".join(parts[-2:])  # main domain and suffix
        return domain

    return "Unknown"


def plotResults(df: DataFrame, fp: Path) -> None:
    print("Sample URLs:")
    print(df["dataAvailabilityLink"].head())

    df["domain"] = df["dataAvailabilityLink"].apply(extract_domain)

    print("Extracted domains:")
    print(df[["dataAvailabilityLink", "domain"]].head())

    domain_counts = df["domain"].value_counts().reset_index()
    domain_counts.columns = ["domain", "count"]

    plt.figure(figsize=(12, 8))
    sns.barplot(x="domain", y="count", data=domain_counts)
    plt.title("Count of Different Artifact Locations")
    plt.xlabel("Domain")
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig(fp)
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
    df = pandas.read_csv(inputPath)

    print("Initial DataFrame:")
    print(df.head())

    df["domain"] = df["dataAvailabilityLink"].apply(extract_domain)
    print("DataFrame with Domain Column:")
    print(df)


if __name__ == "__main__":
    main()
