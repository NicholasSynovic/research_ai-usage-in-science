from pathlib import Path

import click
import pandas
import requests
from bs4 import BeautifulSoup
from pandas import DataFrame
from progress.bar import Bar


def countPapers(inputPath: Path):
    pandas.set_option("display.max_colwidth", None)
    df: DataFrame = pandas.read_parquet(inputPath)
    count = 0

    bar = Bar("Processing Rows", max=len(df))

    for index, row in df.iterrows():
        doi = row["doi"]

        try:
            response = requests.get(doi, timeout=20)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            supporting_info_section = soup.find(id="section5")
            if supporting_info_section:
                supplementary_materials = supporting_info_section.find_all(
                    "div", class_="supplementary-material"
                )
                if supplementary_materials:
                    count += 1
                else:
                    supporting_info_title = soup.find(
                        "h2", string="Supporting information"
                    )
                    if supporting_info_title:
                        supplementary_materials = (
                            supporting_info_title.find_next_sibling(
                                "div", class_="supplementary-material"
                            )
                        )
                        if supplementary_materials:
                            count += 1
            else:
                supporting_info_title = soup.find(
                    "h2", string="Supporting information"
                )
                if supporting_info_title:
                    supplementary_materials = (
                        supporting_info_title.find_next_sibling(
                            "div", class_="supplementary-material"
                        )
                    )
                    if supplementary_materials:
                        count += 1

        except Exception as e:
            print(f"Error processing URL {doi}: {e}")

        bar.next()

    bar.finish()

    return count + "/" + max


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
def main(inputPath: Path) -> None:
    print(countPapers(inputPath))
    # 333/475


if __name__ == "__main__":
    main()
