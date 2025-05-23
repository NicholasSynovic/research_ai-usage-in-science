import sys
from argparse import ArgumentParser, Namespace, _SubParsersAction
from collections import defaultdict
from json import dumps, loads
from math import ceil
from os import getcwd
from pathlib import Path
from typing import Any, List

import pandas
from bs4 import BeautifulSoup, ResultSet, Tag
from pandas import DataFrame, ExcelFile, Series
from progress.bar import Bar
from requests import Response, get

from src import analysis, searchFunc
from src.db import DB
from src.downloader import download
from src.utils import ifFileExistsExit

COMMANDS: set[str] = {
    "init",
    "search",
    "ed",
    "oa",
    "filter",
    "aa",
    "stat",
    "download",
}


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
    initParser.add_argument(
        "-f",
        "--force",
        default=False,
        action="store_true",
        help="Force creating a new database",
        dest="init.force",
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
        choices=["nature", "plos"],
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

    aaParser: ArgumentParser = subparser.add_parser(
        name="author-agreement",
        help="Add the author agreement data to the dataset (Optional Step 5)",
    )
    aaParser.add_argument(
        "-d",
        "--db",
        nargs=1,
        default=Path("aius.sqlite3"),
        type=Path,
        help="Path to AIUS SQLite3 database",
        dest="aa.db",
    )
    aaParser.add_argument(
        "-w",
        "--workbook",
        nargs=1,
        default=Path("author-agreement.xlsx"),
        type=Path,
        help="Path to author agreement Excel (.xlsx) workbook",
        dest="aa.wb",
    )

    statParser: ArgumentParser = subparser.add_parser(
        name="stat",
        help="Generate statistics from the dataset and print to console",
    )
    statParser.add_argument(
        "-d",
        "--db",
        nargs=1,
        default=Path("aius.sqlite3"),
        type=Path,
        help="Path to AIUS SQLite3 database",
        dest="stat.db",
    )

    downloadParser: ArgumentParser = subparser.add_parser(
        name="download",
        help="Download samples of PDF documents",
    )
    downloadParser.add_argument(
        "-d",
        "--db",
        nargs=1,
        default=Path("aius.sqlite3"),
        type=Path,
        help="Path to AIUS SQLite3 database",
        dest="download.db",
    )
    downloadParser.add_argument(
        "-s",
        "--sample",
        nargs=1,
        choices=["author-agreement", "plos-ns"],
        help="Sample of papers to download",
        dest="download.sample",
    )
    downloadParser.add_argument(
        "-o",
        "--output-dir",
        nargs=1,
        default=Path("."),
        type=Path,
        help="Path to save PDFs",
        dest="download.output",
    )
    return parser.parse_args()


def initialize(fp: Path, force: bool = False) -> DB:
    if force is False:
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
    Modifies df2 in place by replacing values in column `c2` with the corresponding
    index values from df1 based on matching values in column `c1`.

    For each value in df1[c1], the function finds matching rows in df2[c2]
    and replaces those values with the index of the value in df1.

    Parameters:
        df1 (DataFrame): Source DataFrame containing the reference values and indices.
        df2 (DataFrame): Target DataFrame whose column will be modified in place.
        c1 (str): Column name in df1 to match values from.
        c2 (str): Column name in df2 whose matching values will be replaced.

    Note:
        - df1[c1] values are assumed to be unique.
        - This operation is performed in-place and does not return anything.
        - May be inefficient for large DataFrames due to the use of a loop.
    """  # noqa: E501
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
                case 1:
                    soup: BeautifulSoup = BeautifulSoup(
                        markup=row["html"],
                        features="lxml",
                    )
                    tags: ResultSet[Tag] = soup.find_all(
                        name="a",
                        attrs={
                            "class920d1b31810b3ad8d86825c7a0496989": "c-card__link"  # noqa: E501
                        },
                    )

                    tag: Tag
                    for tag in tags:
                        url: str = tag.get(key="href")
                        doi: str = NATURE_DOI + url.split("/")[-1]
                        data["document_id"].append(doi)
                        data["response_id"].append(idx)
                case 2:
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
        "Getting document metadata from OpenAlex...",
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

            field: str | None
            for field in fields:
                if field is None:
                    continue

                if len(FIELD_FILTER.intersection([field])) == 1:
                    nsFields.append(field)

            if len(nsFields) >= 2:
                isNS = True

            data["fields"].append(fields.__str__())
            data["natural_science_fields"].append(nsFields.__str__())
            data["is_natural_science"].append(isNS)

            dfs.append(DataFrame(data=data))

            bar.next()

        documentFilterDF: DataFrame = pandas.concat(
            objs=dfs,
            ignore_index=True,
        )

        documentFilterDF.to_sql(
            name="document_filter",
            con=db.engine,
            if_exists="append",
            index=False,
        )


def addAuthorAgreement(dbFP: Path, aaFP: Path) -> None:
    db: DB = DB(fp=dbFP)
    documentDF: DataFrame = db.readTableToDF(table="documents")

    ef: ExcelFile = ExcelFile(path_or_buffer=aaFP, engine="openpyxl")
    df: DataFrame = pandas.read_excel(io=ef, sheet_name="Author Agreement")
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace(" ", "_")
    df.rename(columns={"doi": "document_id"}, inplace=True)

    row: Series
    idx: int
    for idx, row in df.iterrows():
        datum: List[dict[str, str]] = []
        if pandas.isna(obj=row["ptm_reuse_pairings"]):
            continue

        pairSplits: List[str] = row["ptm_reuse_pairings"].split(";")

        pairStr: str
        for pairStr in pairSplits:
            data: dict[str, str] = defaultdict(str)

            pairStr = pairStr.strip()
            model, reuseMethod = pairStr.split(",")
            model = model.replace("[", "").strip()
            reuseMethod = reuseMethod.replace("]", "").strip()

            data["ptm"] = model
            data["reuse_method"] = reuseMethod

            datum.append(data)

        df.at[idx, "ptm_reuse_pairings"] = dumps(obj=datum)

    df["ptm_reuse_pairings"] = df["ptm_reuse_pairings"].fillna(value="[]")

    _mapDFIndexToDFValue(df1=documentDF, df2=df, c1="doi", c2="document_id")

    df.to_sql(
        name="author_agreement",
        con=db.engine,
        if_exists="append",
        index=True,
        index_label="id",
    )


def stats(dbFP: Path, outputDir: Path) -> None:
    def _analysis2json(func, filename: str) -> None:
        outputFP: Path = Path(outputDir, filename)
        func(db=db).to_json(path_or_buf=outputFP, index=False, indent=4)
        print("Saved analysis to:", outputFP)

    db: DB = DB(fp=dbFP)

    print(
        "Total search results from PLOS:",
        analysis.countTotalSearchResultsFromPLOS(db=db),
    )

    print(
        "Total unique search results from PLOS:",
        analysis.countTotalUniqueSearchResultsFromPLOS(db=db),
    )

    print(
        "Total completely unique search results from PLOS:",
        analysis.countTotalCompletelyUniqueSearchResultsFromPLOS(db=db),
    )

    print(
        "Total search results present in two or more search queries:",
        analysis.countTotalUniqueSearchResultsFromPLOS(db=db)
        - analysis.countTotalCompletelyUniqueSearchResultsFromPLOS(db=db),
    )

    print(
        "Total unique search results from PLOS that are also indexed in OpenAlex:",  # noqa: E501
        analysis.countNumberOf_PLOS_OA_PapersPerYear(db=db).values.sum(),
    )

    print(
        "Total unique search results from PLOS that are also indexed in OpenAlex, have at least one citation, and are Natural Science works:",  # noqa: E501
        analysis.countNumberOf_PLOS_OA_NS_PapersPerYear(db=db).values.sum(),
    )

    print("\n===\n")

    _analysis2json(
        analysis.countTotalSearchResultsFromPLOSByKeyword,
        "totalSearchResultsByKeyword_PLOS.json",
    )

    _analysis2json(
        analysis.countTotalUniqueSearchResultsFromPLOSByKeyword,
        "totalUnqiueSearchResultsByKeyword_PLOS.json",
    )

    _analysis2json(
        analysis.countTotalCompletelyUniqueSearchResultsFromPLOSByKeyword,
        "totalCompletelyUnqiueSearchResultsByKeyword_PLOS.json",
    )

    print("\n===\n")

    analysis.plotNumberOf_PLOS_OA_NS_PapersPerYear(
        db=db,
        outputDir=Path(getcwd()),
    )


def main() -> None:
    args: dict[str, Any] = cliParser().__dict__

    argSet: set[str] = set([cmd.split(".")[0] for cmd in args.keys()])

    try:
        arg: str = list(argSet.intersection(COMMANDS))[0]
    except IndexError:
        sys.exit(1)

    match arg:
        case "init":
            initialize(fp=args["init.db"][0], force=args["init.force"])
        case "search":
            search(fp=args["search.db"][0], journal=args["search.journal"][0])
        case "ed":
            extractDocuments(fp=args["ed.db"][0])
        case "oa":
            getOpenAlexMetadata(fp=args["oa.db"][0], email=args["oa.email"][0])
        case "filter":
            filterDocuments(fp=args["filter.db"][0])
        case "aa":
            addAuthorAgreement(dbFP=args["aa.db"][0], aaFP=args["aa.wb"][0])
        case "stat":
            stats(dbFP=args["stat.db"][0], outputDir=Path("."))
        case "download":
            if (
                download(
                    dbFP=args["download.db"][0],
                    sample=args["download.sample"][0],
                    outputDir=args["download.output"][0],
                )
                == 0
            ):
                sys.exit(1)

        case _:
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
