from pathlib import Path

import click
import pandas
from pandas import DataFrame, Series
from progress.bar import Bar
from requests import Response, get

from aius import KEYWORD_LIST, YEAR_LIST
from aius.search.plos import PLOS


def create_urls() -> list[str]:
    urls: list[str] = []
    plos: PLOS = PLOS()

    year: int
    keyword: str
    for year in YEAR_LIST:
        for keyword in KEYWORD_LIST:
            urls.append(
                plos._construct_url(year=year, keyword=keyword, page=1)
                .replace("DATE_NEWEST_FIRST", "MOST_CITED")
                .replace("resultsPerPage=100", "resultsPerPage=1")
            )

    return urls


def get_all_pages(urls: list[str]) -> DataFrame:
    data: dict[str, list[str | Response | dict]] = {
        "url": [],
        "response": [],
        "json": [],
    }

    with Bar("Getting PLOS pilot study pages...", max=len(urls)) as bar:
        for url in urls:
            # Query PLOS URL
            resp: Response = get(
                url=url,
                timeout=60,
            )

            # Write data to data structure
            data["url"].append(url)
            data["response"].append(resp)
            data["json"].append(resp.json()["searchResults"]["docs"])

            bar.next()

    return DataFrame(data=data)


def get_document_ids(df: DataFrame) -> set[str]:
    data: list[str] = []

    json_data: Series = df["json"]

    row: list[dict]
    for row in json_data:
        if len(row) > 0:
            data.append(row[0]["id"])

    return set(data)


@click.command()
@click.option(
    "-o",
    "--output",
    type=lambda x: Path(x).resolve(),
    required=False,
    show_default=True,
    default=Path("pilot_study.pickle").resolve(),
    help="Path to store output Python Pickle file",
)
def main(output: Path) -> None:
    df: DataFrame
    if output.exists():
        # Load data if it exists
        df = pandas.read_pickle(filepath_or_buffer=output)
    else:
        # Query PLOS for data and write to disk
        plos_urls: list[str] = create_urls()
        df: DataFrame = get_all_pages(urls=plos_urls)
        df.to_pickle(path=output)

    # Get the set of PLOS document IDs
    plos_document_ids: set[str] = get_document_ids(df=df)

    # Print the set of PLOS document IDs
    _id: str
    for _id in sorted(plos_document_ids, reverse=True):
        print(_id)


if __name__ == "__main__":
    main()
