from pathlib import Path

import click
import pandas
import requests
from bs4 import BeautifulSoup
from pandas import DataFrame
from progress.bar import Bar


def supportingInfo(inputPath: Path, outputPath: Path) -> DataFrame:
    df: DataFrame = pandas.read_parquet(inputPath)

    results = []
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
                        dataKey = (
                            dataKeyTitle.find("a").text.strip()
                            if dataKeyTitle.find("a")
                            else "N/A"
                        )
                        dataTitle = (
                            dataKeyTitle.get_text(separator=" ")
                            .replace(dataKey, "")
                            .strip()
                        )

                        dataDesc = material.find("p", class_="preSiDOI")
                        dataDescText = (
                            dataDesc.text.strip() if dataDesc else "N/A"
                        )

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

                        results.append(
                            {
                                "ID": rowID,
                                "DOI": doi,
                                "Data Key": dataKey,
                                "Data Title": dataTitle,
                                "Data Desc": dataDescText,
                                "Data URL": dataURL,
                                "Data Type": dataTypeText,
                            }
                        )

                        rowID += 1
        except Exception as e:
            print(f"Error processing URL {doi}: {e}")

        bar.next()

    bar.finish()

    resultsDf = DataFrame(results)

    resultsDf.to_csv(outputPath, index=False)

    return resultsDf


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
    supportingInfo(inputPath, outputPath)


if __name__ == "__main__":
    main()
