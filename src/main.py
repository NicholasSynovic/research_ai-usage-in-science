import sys
from argparse import ArgumentParser, Namespace, _SubParsersAction
from collections import defaultdict
from json import dumps, loads
from math import ceil
from pathlib import Path
from typing import Any, List

import pandas
from bs4 import BeautifulSoup, ResultSet, Tag
from pandas import DataFrame, Series
from progress.bar import Bar
from requests import Response, get

from src import searchFunc
from src.db import DB
from src.utils import ifFileExistsExit

COMMANDS: set[str] = {"init", "search", "ed", "oa", "filter"}


def cliParser() -> Namespace:
    parser: ArgumentParser = ArgumentParser(
        prog="aius",
        description="Identify AI usage in Natural Science research",
    )
    subparser: _SubParsersAction[ArgumentParser] = parser.add_subparsers()

    initParser: ArgumentParser = subparser.add_parser(
        name="init",
        help="Initialize AIUS (Step 0)",
    )
    initParser.add_argument(
        "-d",
        "--db",
        nargs=1,
        default=Path("aius.sqlite3"),
        type=Path,
        help="Path to create AIUS SQLite3 database",
        dest="init.db",
    )

    searchParser: ArgumentParser = subparser.add_parser(
        name="search",
        help="Search Journals (Step 1)",
    )
    searchParser.add_argument(
        "-d",
        "--db",
        nargs=1,
        default=Path("aius.sqlite3"),
        type=Path,
        help="Path to AIUS SQLite3 database",
        dest="search.db",
    )
    searchParser.add_argument(
        "-j",
        "--journal",
        nargs=1,
        default="plos",
        type=str,
        choices=["nature", "plos", "science"],
        help="Journal to search through",
        dest="search.journal",
    )

    edParser: ArgumentParser = subparser.add_parser(
        name="extract-documents",
        help="Extract Documents From Search Responses (Step 2)",
    )
    edParser.add_argument(
        "-d",
        "--db",
        nargs=1,
        default=Path("aius.sqlite3"),
        type=Path,
        help="Path to AIUS SQLite3 database",
        dest="ed.db",
    )

    oaParser: ArgumentParser = subparser.add_parser(
        name="openalex",
        help="Get Document Metadata From OpenAlex (Step 3)",
    )
    oaParser.add_argument(
        "-d",
        "--db",
        nargs=1,
        default=Path("aius.sqlite3"),
        type=Path,
        help="Path to AIUS SQLite3 database",
        dest="oa.db",
    )
    oaParser.add_argument(
        "-e",
        "--email",
        nargs=1,
        type=str,
        help="Email address to access OpenAlex polite pool",
        dest="oa.email",
    )

    filterParser: ArgumentParser = subparser.add_parser(
        name="filter",
        help="Filter For Documents Relevant To This Study (Step 4)",
    )
    filterParser.add_argument(
        "-d",
        "--db",
        nargs=1,
        default=Path("aius.sqlite3"),
        type=Path,
        help="Path to AIUS SQLite3 database",
        dest="filter.db",
    )

    return parser.parse_args()


def initialize(fp: Path) -> DB:
    ifFileExistsExit(fps=[fp])
    db: DB = DB(fp=fp)
    db.createTables()
    db.writeConstants()
    return db


def _mapDFIndexToDFValue(
    df1: DataFrame,
    df2: DataFrame,
    c1: str,
    c2: str,
) -> None:
    """
    Modifies df2 in place
    """
    replacementValues: Series = df1[c1]

    val: Any
    for val in replacementValues:
        df2.loc[df2[c2] == val, c2] = int(
            replacementValues[replacementValues == val].index[0]
        )


def search(fp: Path, journal: str) -> None:
    df: DataFrame | None = None

    db: DB = DB(fp=fp)

    match journal:
        case "nature":
            df = searchFunc.nature()
        case "plos":
            df = searchFunc.plos()
        case "science":
            searchFunc.science()
            return None
        case _:
            return None

    df.rename(columns={"query": "keyword"}, inplace=True)

    yearsDF: DataFrame = db.readTableToDF(table="years")
    keywordsDF: DataFrame = db.readTableToDF(table="keywords")
    journalsDF: DataFrame = db.readTableToDF(table="journals")

    _mapDFIndexToDFValue(yearsDF, df, "year", "year")
    _mapDFIndexToDFValue(
        keywordsDF,
        df,
        "keyword",
        "keyword",
    )
    _mapDFIndexToDFValue(
        journalsDF,
        df,
        "journal",
        "journal",
    )

    df.to_sql(
        name="search_responses",
        con=db.engine,
        if_exists="append",
        index=False,
    )


def extractDocuments(fp: Path) -> None:
    NATURE_DOI: str = "10.1038/"
    dfs: List[DataFrame] = []

    db: DB = DB(fp=fp)

    respDF: DataFrame = db.readTableToDF(table="search_responses")

    row: Series
    with Bar(
        "Extracting documents from search responses...",
        max=respDF.shape[0],
    ) as bar:
        for idx, row in respDF.iterrows():
            data: defaultdict[str, List[str | int]] = defaultdict(list)
            match row["journal"]:
                case 0:
                    soup: BeautifulSoup = BeautifulSoup(
                        markup=row["html"],
                        features="lxml",
                    )
                    tags: ResultSet[Tag] = soup.find_all(
                        name="a",
                        attrs={"class": "c-card__link"},
                    )

                    tag: Tag
                    for tag in tags:
                        url: str = tag.get(key="href")
                        doi: str = NATURE_DOI + url.split("/")[-1]
                        data["document_id"].append(doi)
                        data["response_id"].append(idx)
                case 1:
                    json: dict[str, Any] = loads(row["html"])
                    docs: List[dict[str, Any]] = json["searchResults"]["docs"]

                    doc: dict[str, Any]
                    for doc in docs:
                        doi: str = doc["id"]
                        data["document_id"].append(doi)
                        data["response_id"].append(idx)
                case _:
                    return None
            dfs.append(DataFrame(data=data))
            bar.next()

    searchResultsDF: DataFrame = pandas.concat(objs=dfs, ignore_index=True)

    documentsDF: DataFrame = DataFrame(
        data=searchResultsDF["document_id"].unique(),
        columns=["doi"],
    )

    _mapDFIndexToDFValue(
        df1=documentsDF,
        df2=searchResultsDF,
        c1="doi",
        c2="document_id",
    )

    documentsDF.to_sql(
        name="documents",
        con=db.engine,
        if_exists="append",
        index=False,
    )
    searchResultsDF.to_sql(
        name="search_results",
        con=db.engine,
        if_exists="append",
        index=False,
    )


def getOpenAlexMetadata(fp: Path, email: str, doiCount: int = 25) -> None:
    DOI_URL: str = "https://doi.org/"
    dfs: List[DataFrame] = []

    db: DB = DB(fp=fp)

    documentDF: DataFrame = db.readTableToDF(table="documents")

    documentDF["doi_url"] = documentDF["doi"].apply(lambda x: DOI_URL + x)

    idx: int
    with Bar(
        "Getting document metadata from PLOS...",
        max=ceil(documentDF.shape[0] / 25),
    ) as bar:
        for idx in range(0, documentDF.shape[0], doiCount):
            data: defaultdict[str, List[str | int]] = defaultdict(list)

            _df: DataFrame = documentDF.iloc[
                idx : idx + doiCount  # noqa: E203
            ]
            dois: str = "|".join(_df["doi_url"].to_list())
            url: str = (
                "https://api.openalex.org/works?mailto="
                + email
                + "&filter=doi:"
                + dois
            )
            resp: Response = get(url=url, timeout=60)

            if resp.status_code != 200:
                print(resp.status_code)
                data["document_id"].append("")
                data["url"].append(url)
                data["status_code"].append(resp.status_code)
                data["html"].append("")
                bar.next()
                continue

            document: dict
            for document in resp.json()["results"]:
                data["document_id"].append(
                    document["doi"].replace(DOI_URL, "")
                )
                data["url"].append(url)
                data["status_code"].append(resp.status_code)
                data["html"].append(dumps(obj=document))

            dfs.append(DataFrame(data=data))
            bar.next()

    oaResponsesDF: DataFrame = pandas.concat(objs=dfs, ignore_index=True)

    _mapDFIndexToDFValue(
        df1=documentDF,
        df2=oaResponsesDF,
        c1="doi",
        c2="document_id",
    )

    oaResponsesDF.to_sql(
        name="openalex_responses",
        con=db.engine,
        if_exists="append",
        index=False,
    )


def filterDocuments(fp: Path) -> None:
    FIELD_FILTER: set[str] = {
        "Agricultural and Biological Sciences",
        "Environmental Science",
        "Biochemistry Genetics and Molecular Biology",
        "Immunology and Microbiology",
        "Neuroscience",
        "Earth and Planetary Sciences",
        "Physics and Astronomy",
        "Chemistry",
    }

    dfs: List[DataFrame] = []

    db: DB = DB(fp=fp)

    oaResponses: DataFrame = db.readTableToDF(table="openalex_responses")

    row: Series
    with Bar("Filtering documents...", max=oaResponses.shape[0]) as bar:
        for idx, row in oaResponses.iterrows():
            nsFields: List[str] = []
            fields: List[str | None] = []
            isNS: bool = False

            data: defaultdict[str, List[Any]] = defaultdict(list)

            json: dict = loads(s=row["html"])

            data["document_id"].append(row["document_id"])
            data["openalex_response_id"].append(idx)
            data["retracted"].append(json["is_retracted"])
            data["open_access"].append(json["open_access"]["is_oa"])
            data["cited_by_count"].append(json["cited_by_count"])

            topic: dict
            for topic in json["topics"]:
                fields.append(topic["field"]["display_name"])

            data["fields"].append(fields)

            field: str | None
            for field in fields:
                if field is None:
                    continue

                if len(FIELD_FILTER.intersection([field])) == 1:
                    nsFields.append(field)

            data["natural_science_fields"].append(nsFields)

            if len(nsFields) >= 2:
                isNS = True

            data["is_natural_science"].append(isNS)

            dfs.append(DataFrame(data=data))

            bar.next()

        df: DataFrame = pandas.concat(objs=dfs, ignore_index=True)
        print(df)
        print(df["is_natural_science"].value_counts())


def main() -> None:
    args: dict[str, Any] = cliParser().__dict__

    argSet: set[str] = set([cmd.split(".")[0] for cmd in args.keys()])

    try:
        arg: str = list(argSet.intersection(COMMANDS))[0]
    except IndexError:
        sys.exit(0)

    match arg:
        case "init":
            initialize(fp=args["init.db"][0])
        case "search":
            search(fp=args["search.db"][0], journal=args["search.journal"][0])
        case "ed":
            extractDocuments(fp=args["ed.db"][0])
        case "oa":
            getOpenAlexMetadata(fp=args["oa.db"][0], email=args["oa.email"][0])
        case "filter":
            filterDocuments(fp=args["filter.db"][0])

    sys.exit(0)


if __name__ == "__main__":
    main()
