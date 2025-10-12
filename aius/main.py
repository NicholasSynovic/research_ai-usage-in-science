"""
Main entry point to `aius`.

Copyright 2025 (C) Nicholas M. Synovic

"""

import sys
from collections.abc import Iterable
from itertools import product
from pathlib import Path
from typing import Any

import pandas as pd
from pandas import DataFrame

import aius
from aius.cli import CLI
from aius.db import DB
from aius.filter_documents import NaturalScienceFilter
from aius.identify_documents import PLOSPaperIdentifier
from aius.load_author_agreement import LoadAuthorAgreement
from aius.load_pilot_study import LoadPilotStudy
from aius.openalex import OpenAlex
from aius.pandoc import PandocAPI
from aius.retrieve_content import RetrieveContent
from aius.search import search
from aius.search.plos import PLOS


def create_keyword_year_product() -> Iterable:
    """
    Generate all combinations of keywords and years.

    This function utilizes the `itertools.product` to create a Cartesian product
    of two lists: `aius.KEYWORD_LIST`, which contains various search terms, and
    `aius.YEAR_LIST`, encompassing different publication years. The output is an
    iterable that can be directly used in loops, list comprehensions, or any
    context requiring combinations of keywords with years.

    Returns:
        Iterable[tuple]: An iterator yielding tuples where each tuple consists
        of a keyword from `aius.KEYWORD_LIST` and a year from `aius.YEAR_LIST`.
        This allows for efficient generation of all possible keyword-year pairs
        without explicitly constructing them in memory.

    Notes:
        The use of this function is particularly useful in scenarios where
        operations need to be performed across multiple combinations of keywords
        and years, such as filtering documents, generating reports, or preparing
        datasets for analysis. It abstracts away the manual iteration over these
        combinations, providing a concise and efficient means to access all
        possible pairs.

    Example:
        >>> from your_module import create_keyword_year_product
        >>> for keyword, year in create_keyword_year_product():
        ...     print(f"Keyword: {keyword}, Year: {year}")
        Keyword: 'AI' Year: 2018
        Keyword: 'AI' Year: 2019
        ...
        Keyword: 'Quantum Computing' Year: 2023

    """
    return product(aius.KEYWORD_LIST, aius.YEAR_LIST)


def main() -> None:  # noqa: PLR0914
    """
    Orchestrate the execution of the `aius` CLI commands.

    This function serves as the entry point for running the suite of tools
    provided by the AI-Util-Suite. It parses command-line arguments, selects and
    initializes the appropriate sub-command based on user input, and executes
    the corresponding functionality to process, analyze, or store data according
    to the selected operation.

    The main function encapsulates the workflow of the CLI application, ensuring
    that each step from parsing inputs to executing specific operations is
    handled in a structured manner. It leverages Python's `match` statement for
    conditional execution based on parsed arguments, facilitating clean and
    readable code by directly mapping command names to their respective
    processing logic.

    """
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
            df: DataFrame = search(
                journal_search=PLOS(),
                keyword_year_products=create_keyword_year_product(),
            )

            # Write data to the database
            df.to_sql(
                name="plos_searches",
                con=db.engine,
                if_exists="append",
                index=True,
                index_label="_id",
            )

        case "identify_documents":  # Identify papers from PLOS searches
            # Get search data
            plos_search_df: DataFrame = pd.read_sql_table(
                table_name="plos_searches",
                con=db.engine,
            )

            # Identify documents from the search results and create a mapping
            # between search result and documents
            ppi: PLOSPaperIdentifier = PLOSPaperIdentifier(
                plos_search_df=plos_search_df
            )

            # Write PLOS paper dois to the database
            ppi.plos_unique_papers_df.to_sql(
                name="plos_paper_dois",
                con=db.engine,
                if_exists="append",
                index=True,
                index_label="_id",
            )

            # Write PLOS searches to paper doi mapping to the database
            ppi.searches_to_papers_mapping.to_sql(
                name="plos_searches_to_paper_dois",
                con=db.engine,
                if_exists="append",
                index=True,
                index_label="_id",
            )

        case "openalex":  # Get paper metadata from OpenAlex
            # Get the email address from the CLI
            email: str = args[f"{subparser}.email"][0]

            # Get papers data
            doi_df: DataFrame = pd.read_sql_table(
                table_name="plos_paper_dois",
                con=db.engine,
                index_col="_id",
            )

            # Instantiate OpenAlex object
            oa: OpenAlex = OpenAlex(email=email, doi_df=doi_df)

            oa.metadata.to_sql(
                name="plos_paper_openalex_metadata",
                con=db.engine,
                if_exists="append",
                index=True,
                index_label="_id",
            )

        case "doucment_filter":
            # Filter for documents
            ns_papers: DataFrame = NaturalScienceFilter(db=db).df

            # Write data
            ns_papers.to_sql(
                name="plos_natural_science_papers",
                con=db.engine,
                if_exists="append",
                index=True,
                index_label="_id",
            )

        case "content_retriever":
            # Get All of PLOS zip file path
            archive_path: Path = args[f"{subparser}.fp"][0]
            pandoc_url: str = args[f"{subparser}.pandoc_url"][0]

            # Instantiate PandocAPI
            pandoc_api: PandocAPI = PandocAPI(pandoc_url=pandoc_url)

            # Retrieve content from the zip file
            rc: RetrieveContent = RetrieveContent(
                db=db, archive_path=archive_path, pandoc_api=pandoc_api
            )

            # Write data
            rc.content_df.to_sql(
                name="plos_natural_science_paper_content",
                con=db.engine,
                if_exists="append",
                index=True,
                index_label="_id",
            )

        case "load_pilot_study":
            pilot_study_csv: Path = args[f"{subparser}.fp"][0]

            lps: LoadPilotStudy = LoadPilotStudy(
                pilot_study_csv=pilot_study_csv,
                db=db,
            )

            lps.df.to_sql(
                name="plos_pilot_study_papers",
                con=db.engine,
                if_exists="append",
                index=True,
                index_label="_id",
            )

        case "load_author_agreement":
            author_agreement_csv: Path = args[f"{subparser}.fp"][0]

            laa: LoadAuthorAgreement = LoadAuthorAgreement(
                pilot_study_csv=author_agreement_csv,
                db=db,
            )

            laa.df.to_sql(
                name="plos_author_agreement_papers",
                con=db.engine,
                if_exists="append",
                index=True,
                index_label="_id",
            )

        case "load_llm_prompts":
            aius.LLM_PROMPTS.to_sql(
                name="llm_prompts",
                con=db.engine,
                if_exists="append",
                index=True,
                index_label="_id",
            )

        case _:
            sys.exit(1)


if __name__ == "__main__":
    main()
