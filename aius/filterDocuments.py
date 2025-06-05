from json import loads
from pathlib import Path
from typing import List

import click
import pandas
from pandas import DataFrame, Series
from progress.bar import Bar
from requests import Response, get

from src.filter import FIELD_FILTER
from src.utils import ifFileExistsExit


def getOA(email: str, doi: str) -> Response:
    url: str = f"https://api.openalex.org/works/{doi}?mailto={email}"
    return get(url=url, timeout=60)


def parseOAResponse(doi: str, resp: Response) -> None | DataFrame:
    data: dict[str, List[str | int]] = {
        "doi": [doi],
        "api_call": [resp.url],
        "status_code": [resp.status_code],
        "json": [],
    }

    if resp.status_code != 200:
        return None
    else:
        data["json"].append(resp.content.decode(errors="ignore"))

    return DataFrame(data=data)


def extractOACitedByCount(df: DataFrame) -> int:
    jsonStr: str = df["json"][0]
    jsonDict: dict = loads(s=jsonStr)
    return jsonDict["cited_by_count"]


def extractOATopicFields(df: DataFrame) -> List[str]:
    data: List[str] = []

    jsonStr: str = df["json"][0]
    jsonDict: dict = loads(s=jsonStr)

    topic: dict[str, str]
    for topic in jsonDict["topics"]:
        data.append(topic["field"]["display_name"])

    return data


def identifyIfNaturalScience(topics: List[str]) -> bool:
    if len(FIELD_FILTER.intersection(topics)) < 2:
        return False
    return True


def runner(df: DataFrame, email: str) -> DataFrame:
    data: List[Series] = []

    with Bar(
        "Iterating through documents to find Natural Science documents...",
        max=df.shape[0],
    ) as bar:
        row: Series
        for _, row in df.iterrows():
            resp: Response = getOA(email=email, doi=row["doi"])

            oaDF: None | DataFrame = parseOAResponse(
                doi=row["doi"],
                resp=resp,
            )

            if oaDF is None:
                bar.next()
                continue

            citedByCount: int = extractOACitedByCount(df=oaDF)

            if citedByCount == 0:
                bar.next()
                continue

            topics: List[str] = extractOATopicFields(df=oaDF)
            if len(topics) < 2:
                bar.next()
                continue

            isNaturalScienceDocument: bool = identifyIfNaturalScience(
                topics=topics,
            )
            if isNaturalScienceDocument:
                data.append(row.to_frame().T)

            bar.next()

    return pandas.concat(objs=data, ignore_index=True)


@click.command()
@click.option(
    "-e",
    "--email",
    "email",
    required=True,
    help="Email to access OpenAlex polite pool",
    type=str,
)
@click.option(
    "-j",
    "--journal",
    "journal",
    required=True,
    help="Journal of search results",
    type=click.Choice(
        choices=["plos", "nature"],
        case_sensitive=False,
    ),
)
@click.option(
    "-i",
    "--input",
    "inputPath",
    required=True,
    help="Search results file",
    type=click.Path(
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
)
@click.option(
    "-o",
    "--output",
    "outputPath",
    required=True,
    help="Apache Parquet file to write Natrual Science documents",
    type=click.Path(
        exists=False,
        file_okay=True,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
)
def main(email: str, journal: str, inputPath: Path, outputPath: Path) -> None:
    """
    Given the metadata of documents from a journal, output a Pandas DataFrame that of documents that are categorized as Natural Sciences by OpenAlex as a as an Apache Parquet file.

    Only documents that have an OpenAlex listing, are cited at least once, and have two or more topics assigned by OpenAlex are considered in the filtering process.

    These documents are meant to be post-processed for usage in other scripts.

    While the data outputted from this script can be leveraged independently, it is better to use this data in the following pipeline:

    aius-search-journal -> aius-extract-documents -> **aius-filter-documents** -> aius-sample-documents -> aius-download-documents
    """  # noqa: E501
    ifFileExistsExit(fps=[outputPath])

    df: DataFrame = pandas.read_parquet(path=inputPath, engine="pyarrow")
    uniqueDF: DataFrame = df.drop_duplicates(
        subset="doi",
        keep="first",
        ignore_index=False,
    )

    nsDocuments: Series = runner(df=uniqueDF, email=email)

    nsDocuments.to_parquet(path=outputPath, engine="pyarrow")


if __name__ == "__main__":
    main()
