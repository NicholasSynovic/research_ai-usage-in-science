from pathlib import Path
from typing import List
from urllib.parse import urlparse

import click
import pandas
import requests
from bs4 import BeautifulSoup
from pandas import DataFrame
from progress.bar import Bar


def getUrls(inputPath: Path) -> DataFrame:
    df: DataFrame = pandas.read_parquet(inputPath)

    urlList = []
    dataTypeList = []
    bar = Bar("Processing Rows", max=len(df))
    rowID = 1

    for _, row in df.iterrows():
        doi = row["doi"]

        try:
            response = requests.get(doi, timeout=20)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            supportingInfoSection = soup.find(id="section5")
            if not supportingInfoSection:
                supportingInfoTitle = soup.find(
                    "h2", string="Supporting information"
                )
                supportingInfoSection = (
                    supportingInfoTitle.find_next_sibling()
                    if supportingInfoTitle
                    else None
                )

            if supportingInfoSection:
                supplementaryMaterials = supportingInfoSection.find_all(
                    "div", class_="supplementary-material"
                )
                for material in supplementaryMaterials:
                    dataKeyTitle = material.find(
                        "h3", class_="siTitle title-small"
                    )
                    if dataKeyTitle:
                        dataURL = (
                            material.find("p", class_="siDoi").find("a")[
                                "href"
                            ]
                            if material.find("p", class_="siDoi")
                            else "N/A"
                        )
                        dataType = material.find("p", class_="postSiDOI")
                        dataTypeText = (
                            dataType.text.strip() if dataType else "N/A"
                        )
                        urlList.append(dataURL)
                        dataTypeList.append(dataTypeText)

                        rowID += 1
        except Exception as e:
            print(f"Error processing URL {doi}: {e}")

        bar.next()

    bar.finish()

    return urlList, dataTypeList


def extractDomains(urlList: List[str], outputPath: Path) -> List[str]:
    domains = []

    for url in urlList:
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            domains.append(domain)
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            domains.append("N/A")  # In case of an error, append "N/A"

    # Save the domains to a CSV file
    domains_df = pandas.DataFrame({"URL": urlList, "Domain": domains})
    domains_df.to_csv(outputPath, index=False)

    return domains


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
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
    required=True,
    help="Path to a csv file",
)
def main(inputPath: Path, outputPath: Path) -> None:
    urlList: List = getUrls(inputPath)
    extractDomains(urlList, outputPath)


if __name__ == "__main__":
    main()
