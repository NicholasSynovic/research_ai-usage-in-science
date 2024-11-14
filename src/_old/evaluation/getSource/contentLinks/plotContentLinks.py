from pathlib import Path
from typing import List
from urllib.parse import urlparse

import click
import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from pandas import DataFrame, Series


def plotBarValues(data: dict) -> None:
    for i, (_, value) in enumerate(zip(data.keys(), data.values())):
        plt.text(
            i,
            value + 0.25,
            str(int(value)),
            ha="center",
            color="black",
        )


def extractDomains(df: DataFrame) -> DataFrame:
    domains = []
    row: Series
    for _, row in df.iterrows():
        try:
            parsed_url = urlparse(row["link"])
            domain = parsed_url.netloc
            domains.append(domain)
        except Exception as e:
            print(f"Error processing URL {row['link']}: {e}")
            domains.append("N/A")  # if blank append N/A
    data: dict[str, List[str]] = {
        "doi": df["doi"],
        "link": df["link"],
        "domain": domains,
    }
    return DataFrame(data=data)


def githubLinks(df: DataFrame) -> DataFrame:
    githubDF = df[df["domain"].str.contains("github")]

    githubDF = githubDF.drop(columns=["domain"])

    return githubDF


def plot(df: DataFrame, output: str) -> None:
    if "link" not in df.columns:
        raise ValueError("The CSV file must contain a 'link' column.")

    counts = df["link"].value_counts()

    topDomains = counts.head(10).reset_index()
    topDomains.columns = ["link", "Count"]

    plt.figure(figsize=(12, 8))

    sns.barplot(
        x="link",
        y="Count",
        data=topDomains,
        palette="viridis",
        hue="link",
        dodge=False,
    )

    plt.xlabel("Domain")
    plt.ylabel("Frequency")

    plotBarValues(topDomains.set_index("link")["Count"].to_dict())

    plt.title("Top 10 Most Occurring Domains of External Paper Links")
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
        exists=False,
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
    df: DataFrame = pandas.read_csv(inputPath)
    tranformDF: DataFrame = extractDomains(df=df)

    ghDF: DataFrame = githubLinks(df=tranformDF)
    # print(ghDF.sample(n=5, random_state=42))
    plot(ghDF, outputPath)


if __name__ == "__main__":
    main()
