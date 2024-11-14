from pathlib import Path
from urllib.parse import urlparse

import click
import pandas
from pandas import DataFrame


def extractDomain(url: str) -> str:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain


def addCol(df: DataFrame):
    df.insert(4, "domain", None)

    max_iterations = 10
    iteration_count = 0

    for index, row in df.iterrows():
        if iteration_count >= max_iterations:
            break
        url: str = row["dataAvailabilityLink"]
        # print(url)
        domain = extractDomain(url)
        print(domain)
        df.at[index, "domain"] = domain
        iteration_count += 1


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
    help="Path to a csv file or urls",
)
def main(inputPath: Path) -> None:
    # url = "http://AzulEye.github.io/HomogeneousSetsFinder"
    # print(extractDomain(url))

    df = pandas.read_csv(inputPath)
    addCol(df)
    print(df.columns)


if __name__ == "__main__":
    main()
