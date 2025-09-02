import sys
from itertools import product
from pathlib import Path
from typing import Any, Iterable, Literal

from pandas import DataFrame

import aius
from aius.cli import CLI
from aius.init import initialize
from aius.search import JournalSearch, search_all_keyword_year_products
from aius.search.nature import Nature
from aius.search.plos import PLOS


def get_subparser_keyword_from_namespace(namespace: dict[str, list[Any]]) -> str:
    return next(iter(namespace.keys())).split(sep=".")[0]


def instantiate_journal_search(
    journal_name: Literal["plos", "nature"],
) -> JournalSearch:
    if journal_name == "plos":
        return PLOS()
    else:
        return Nature()


def create_keyword_year_product() -> Iterable:
    return product(aius.KEYWORD_LIST, aius.YEAR_LIST)


def main() -> None:
    # Parse command line args
    cli: CLI = CLI()
    namespace: dict[str, Any] = cli.parse().__dict__
    subparser_keyword: str = get_subparser_keyword_from_namespace(
        namespace=namespace,
    )

    # Get the database path
    db_path: Path = namespace[f"{subparser_keyword}.db"]

    match subparser_keyword:
        case "init":  # Initialize the application
            error_code: int = initialize(db_path=db_path)
            if error_code == -1:
                print("ERROR CREATING DATABASE: File already exists")
                sys.exit(2)

        case "search":  # Search journals for papers
            # Get the journal class
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
            print(data_df)

        case _:
            sys.exit(1)


if __name__ == "__main__":
    main()
