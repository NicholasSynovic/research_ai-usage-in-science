from pathlib import Path

import click
import pandas
import requests
from bs4 import BeautifulSoup
from pandas import DataFrame
from progress.bar import Bar


def getDataSource(inputPath: Path, ouputPath: Path):
    pandas.set_option("display.max_colwidth", None)
    df: DataFrame = pandas.read_parquet(inputPath)
    results = []

    bar = Bar("Processing Rows", max=len(df))

    for index, row in df.iterrows():
        doi = row["doi"]
        url = row["url"]

        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve URL {url}: {e}")
            results.append(
                {
                    "doi": doi,
                    "url": " " + url,
                    "dataAvailabilityText": " ",
                    "dataAvailabilityLink": " ",
                }
            )
            bar.next()
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        dataURL = ""
        dataAvailability = ""

        p_tags = soup.find_all("p")
        for p_tag in p_tags:
            strong_tag = p_tag.find("strong")
            if strong_tag and "Data Availability:" in strong_tag.text:
                dataAvailability = p_tag.get_text(separator=" ", strip=True)

                a_tag = p_tag.find("a", href=True)
                if a_tag:
                    dataURL = a_tag["href"]
                break

        results.append(
            {
                "doi": doi,
                "url": " " + url,
                "dataAvailabilityText": " " + dataAvailability,
                "dataAvailabilityLink": " " + dataURL,
            }
        )
        bar.next()

    bar.finish()

    resultDF = pandas.DataFrame(results)
    resultDF.to_csv(ouputPath, index=False)


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
    help="Path to a transformed set of papers",
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
    help="Path to store data in CSV format",
)
def main(inputPath: Path, outputPath: Path) -> None:
    getDataSource(inputPath, outputPath)


if __name__ == "__main__":
    main()
