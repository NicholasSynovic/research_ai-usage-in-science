"""
Main entry point to `aius`

Copyright 2025 (C) Nicholas M. Synovic

"""

import sys
from itertools import product
from pathlib import Path
from typing import Any, Iterable, Literal

import pandas
from pandas import DataFrame

import aius
import aius.filter as aius_filter
import aius.search as aius_search
import aius.search.plos as plos_search
from aius.cli import CLI
from aius.db import DB
from aius.extract_documents import JournalExtractor
from aius.openalex import OpenAlex


def create_keyword_year_product() -> Iterable:
    return product(aius.KEYWORD_LIST, aius.YEAR_LIST)


def main() -> None:
    # Parse command line args
    cli: CLI = CLI()
    args: dict[str, Any] = cli.parse

    # Get the subparser used
    subparser: str = next(iter(args.keys())).split(sep=".")[0]

    # Instantiate the database
    db: DB = DB(db_path=args[f"{subparser}.db"][0])

    match subparser:
        case "search_plos":  # Search PLOS for papers
            # Search PLOS
            df: DataFrame = aius_search.search(
                journal_search=plos_search.PLOS(),
                keyword_year_products=create_keyword_year_product(),
            )

            # Write data to the database
            df.to_sql(
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

        case _:
            sys.exit(1)


if __name__ == "__main__":
    main()
