from aius.cli import CLI
from aius.init import initialize
from typing import Any
import sys
from pathlib import Path
from aius.search import JournalSearch
from aius.search.plos import PLOS
from aius.search.nature import Nature
from typing import Literal


def get_subparser_keyword_from_namespace(namespace: dict[str, list[Any]]) -> str:
    return next(iter(namespace.keys())).split(sep=".")[0]


def instantiate_journal_search(
    journal_name: Literal["plos", "nature"],
) -> JournalSearch:
    if journal_name == "plos":
        return PLOS()
    else:
        return Nature()


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
            journal_search: JournalSearch = instantiate_journal_search(
                journal_name=namespace["search.journal"],
            )

        case _:
            sys.exit(1)


if __name__ == "__main__":
    main()
