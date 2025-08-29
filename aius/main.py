from aius.cli import CLI
from aius.init import initialize
from typing import Any
import sys
from pathlib import Path


def get_subparser_keyword_from_namespace(namespace: dict[str, list[Any]]) -> str:
    return next(iter(namespace.keys())).split(sep=".")[0]


def main() -> None:
    cli: CLI = CLI()
    namespace: dict[str, Any] = cli.parse().__dict__
    subparser_keyword: str = get_subparser_keyword_from_namespace(
        namespace=namespace,
    )

    match subparser_keyword:
        case "init":
            db_path: Path = namespace[f"{subparser_keyword}.db"]
            error_code: int = initialize(db_path=db_path)
            if error_code == -1:
                print("ERROR CREATING DATABASE: File already exists")
                sys.exit(2)

        case _:
            sys.exit(1)


if __name__ == "__main__":
    main()
