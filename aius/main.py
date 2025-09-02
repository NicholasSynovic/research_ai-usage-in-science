import sys
from itertools import product
from pathlib import Path
from typing import Any, Iterable, Literal

from pandas import DataFrame

import aius
from aius.cli import CLI
from aius.db import DB
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

    # Instantiate the database
    db_path: Path = namespace[f"{subparser_keyword}.db"][0]
    db: DB = DB(db_path=db_path)

    match subparser_keyword:
        case "search":  # Search journals for papers
            # Get the total number of existing rows of the `search` table
            row_count: int = db.get_last_row_id(table_name="searches")

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

        case _:
            sys.exit(1)


if __name__ == "__main__":
    main()
