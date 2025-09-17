import sys
from itertools import product
from pathlib import Path
from typing import Any, Iterable, Literal

import pandas
from pandas import DataFrame

import aius
import aius.download.plos as plos_download
import aius.filter as aius_filter
import aius.search.nature as nature_search
import aius.search.plos as plos_search
from aius.cli import CLI
from aius.db import DB
from aius.extract_documents import JournalExtractor
from aius.openalex import OpenAlex
from aius.search import JournalSearch, search_all_keyword_year_products


def get_subparser_keyword_from_namespace(namespace: dict[str, list[Any]]) -> str:
    return next(iter(namespace.keys())).split(sep=".")[0]


def initialize_db(db_path: Path) -> DB:
    return DB(db_path=db_path)


def instantiate_journal_search(
    journal_name: Literal["plos", "nature"],
) -> JournalSearch:
    if journal_name == "plos":
        return plos_search.PLOS()
    else:
        return nature_search.Nature()


def create_keyword_year_product() -> Iterable:
    return product(aius.KEYWORD_LIST, aius.YEAR_LIST)


def main() -> None:
    # Parse command line args
    cli: CLI = CLI()
    namespace: dict[str, Any] = cli.parse().__dict__
    subparser_keyword: str = get_subparser_keyword_from_namespace(
        namespace=namespace,
    )

    # Instantiate the database
    try:
        db_path: Path = namespace[f"{subparser_keyword}.db"][0]
    except TypeError:
        db_path: Path = namespace[f"{subparser_keyword}.db"]

    db: DB = DB(db_path=db_path)

    match subparser_keyword:
        case "search":  # Search journals for papers
            # Get the total number of existing rows of the `search` table
            row_count: int = db.get_last_row_id(table_name="searches")

            # Get the journal class
            journal_search: JournalSearch = instantiate_journal_search(
                journal_name=namespace["search.journal"][0],
            )

            # Create an extended list of keywords and years
            keyword_year_products = create_keyword_year_product()

            # Iterate through products
            data_df: DataFrame = search_all_keyword_year_products(
                journal_search=journal_search,
                keyword_year_products=keyword_year_products,
            )

            # Update index to accomodate for the existing row count if row_count > 0
            if row_count > 0:
                # Offset by 1 to accomodate 0th index
                data_df.index += row_count + 1

            # Write data to the database
            data_df.to_sql(
                name="searches",
                con=db.engine,
                if_exists="append",
                index=True,
                index_label="_id",
            )

        case "ed":  # Extract papers from searches
            # Instantiate the database
            db: DB = DB(db_path=db_path)

            # Get search data
            search_data: DataFrame = pandas.read_sql_table(
                table_name="searches",
                con=db.engine,
            )

            # Get the journal extractor class
            journal_extractor: JournalExtractor = JournalExtractor(
                search_data=search_data,
            )

            # Extract papers
            papers_df: DataFrame = journal_extractor.extract_all_papers()

            # Organize papers
            unique_papers_df: DataFrame
            search_paper_relationships: DataFrame
            unique_papers_df, search_paper_relationships = (
                journal_extractor.organize_papers(
                    papers_df=papers_df,
                )
            )

            # Write data to the database
            unique_papers_df.to_sql(
                name="papers",
                con=db.engine,
                if_exists="append",
                index=True,
                index_label="_id",
            )
            search_paper_relationships.to_sql(
                name="searches_to_papers",
                con=db.engine,
                if_exists="append",
                index=True,
                index_label="_id",
            )

        case "oa":  # Get paper metadata from OpenAlex
            # Get the email address from the CLI
            email: str = namespace[f"{subparser_keyword}.email"][0]

            # Instantiate the database
            db: DB = DB(db_path=db_path)

            # Get papers data
            papers_df: DataFrame = pandas.read_sql_table(
                table_name="papers", con=db.engine, index_col="_id"
            )

            # Instantiate OpenAlex object
            oa: OpenAlex = OpenAlex(email=email, papers_df=papers_df)

            # Request for metadata from OpenAlex
            oa_df: DataFrame = oa.get_metadata()

            # Write data to database
            oa_df.to_sql(
                name="openalex",
                con=db.engine,
                if_exists="append",
                index=True,
                index_label="_id",
            )

        case "filter":
            # Instantiate the database
            db: DB = DB(db_path=db_path)

            # Get data
            data_df: DataFrame = aius_filter.get_papers_openalex_data(db=db)

            # Apply filter
            ns_data: DataFrame = aius_filter.apply_filters(data_df=data_df)

            # Drop irrelevant columns
            ns_papers: DataFrame = ns_data[["paper_id"]]

            # Write data
            ns_papers.to_sql(
                name="ns_papers",
                con=db.engine,
                if_exists="append",
                index=True,
                index_label="_id",
            )

        case "download":
            # Instantiate the database
            db: DB = DB(db_path=db_path)

            # Get data
            sql_query: str = """
                SELECT DISTINCT s.journal, p.doi FROM searches s
                JOIN searches_to_papers sbt ON s._id = sbt.search_id
                JOIN ns_papers ns ON ns.paper_id = sbt.paper_id
                JOIN papers p ON p._id = ns.paper_id;
            """
            data_df: DataFrame = pandas.read_sql_query(
                sql=sql_query,
                con=db.engine,
            )

            # Split the data into PLOS and Nature data
            plos_data_df: DataFrame = data_df[data_df["journal"] == "plos"]
            nature_data_df: DataFrame = data_df[data_df["journal"] == "nature"]

            # Handle PLOS data first

            # Download and store PLOS data
            plos_downloader: plos_download.PLOS = plos_download.PLOS(
                paper_dois=plos_data_df,
            )

            # Download  JATS XML URLs

            breakpoint()
            quit()

            # Create downloader object
            downloader: Downloader = Downloader(
                data=data_df,
                pdf_dir=namespace["download.directory"][0],
            )

            # Download papers
            downloader.download()

        case _:
            sys.exit(1)


if __name__ == "__main__":
    main()
