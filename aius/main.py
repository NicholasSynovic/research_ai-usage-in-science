"""
Main entry point into AIUS.

Copyright 2025 (C) Nicholas M. Synovic

"""

from aius.cli import CLI, get_subparser_keyword
from argparse import Namespace


def main() -> None:
    cli: CLI = CLI()
    args: Namespace = cli.parse_cli()

    subparser_keyword: str = get_subparser_keyword(args=args)

    print(subparser_keyword)


if __name__ == "__main__":
    main()
