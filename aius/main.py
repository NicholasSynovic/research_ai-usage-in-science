import sys
from itertools import product
from pathlib import Path
from typing import Any, Iterable, Literal

from pandas import DataFrame

import aius
import aius.extract_documents.plos as plos_extractor
import aius.search.nature as nature_search
import aius.search.plos as plos_search
from aius.cli import CLI
from aius.db import DB
from aius.extract_documents import JournalExtractor
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


def instantiate_journal_extractor(
    journal_name: Literal["plos", "nature"],
) -> JournalExtractor:
    if journal_name == "plos":
        return plos_extractor.PLOS()
    else:
        return None


def main() -> None:
    # Parse command line args
    cli: CLI = CLI()
    namespace: dict[str, Any] = cli.parse().__dict__
    subparser_keyword: str = get_subparser_keyword_from_namespace(
        namespace=namespace,
    )

    # # Instantiate the database
    db_path: Path = namespace[f"{subparser_keyword}.db"]
    db: DB = initialize_db(db_path=db_path)

    match subparser_keyword:
        case "search":  # Search journals for papers
            # Get the number of already existing rows from the `search` table
            # Get the journal search class
            journal_search: JournalSearch = instantiate_journal_search(
                journal_name=namespace["search.journal"],
            )

            # Create an extended list of keywords and years
            keyword_year_products = create_keyword_year_product()

            # Iterate through products
            data_df: DataFrame = search_all_keyword_year_products(
                journal_search=journal_search,
                keyword_year_products=keyword_year_products,
            )

            # Write data to the database
            data_df.to_sql(
                name="search",
                con=db.engine,
                if_exists="append",
                index=True,
                index_label="_id",
            )

        case "ed":  # Extract papers from searches
            # Instantiate the database
            db: DB = DB(db_path=db_path)

            # Get the journal extractor class
            journal_extractor: JournalExtractor = instantiate_journal_extractor(
                journal_name=namespace["ed.journal"],
            )

            # Extract papers
            journal_extractor.extract_all_papers()

            # Write data to the database

        case _:
            sys.exit(1)


if __name__ == "__main__":
    main()
