"""
Handle command line argument parsing.

Copyright 2025 (C) Nicholas M. Synovic

"""

from argparse import ArgumentParser, Namespace, _SubParsersAction
from importlib.metadata import version
from pathlib import Path

import aius


class CLI:
    def __init__(self) -> None:
        # Set common CLI argument help strings
        self.db_help: str = "Database path"

        # Set CLI default values
        self.database_path: Path = Path(f"./{aius.PROGRAM_NAME}.sqlite3").resolve()

        # Instantiate top-level and sub-parsers
        self.parser: ArgumentParser = ArgumentParser(
            prog=aius.PROGRAM_NAME,
            description=aius.PROGRAM_DESCRIPTION,
            epilog=aius.PROGRAM_EPILOG,
        )
        self.subparsers: _SubParsersAction[ArgumentParser] = self.parser.add_subparsers(
            prog=aius.PROGRAM_NAME,
        )

        # Create sub-parsers
        self.add_search()  # Search journals for papers
        self.add_extract_documents()  # Extract documents from journal search
        self.add_openalex()  # Get document metadata from OpenAlex
        self.add_document_filter()  # Filter for Natural Science documents

        # Add version argument
        self.parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=version(distribution_name=aius.MODULE_NAME),
        )

    def _resolve_path(self, path_string: str) -> Path:
        return Path(path_string).resolve()

    def add_search(self) -> None:
        search_parser: ArgumentParser = self.subparsers.add_parser(
            name="search",
            help="Search journals for papers with keywords",
            description="Step 1",
        )

        search_parser.add_argument(
            "-d",
            "--db",
            nargs=1,
            default=self.database_path,
            type=self._resolve_path,
            help=self.db_help,
            dest="search.db",
        )

        search_parser.add_argument(
            "-j",
            "--journal",
            nargs=1,
            type=str,
            required=True,
            choices=["nature", "plos"],
            help="Journal to search through",
            dest="search.journal",
        )

    def add_extract_documents(self) -> None:
        extract_documents_parser: ArgumentParser = self.subparsers.add_parser(
            name="extract-documents",
            help="Extract documents from journal searches",
            description="Step 2",
        )

        extract_documents_parser.add_argument(
            "-d",
            "--db",
            nargs=1,
            default=self.database_path,
            type=self._resolve_path,
            help=self.db_help,
            dest="ed.db",
        )

    def add_openalex(self) -> None:
        openalex_parser: ArgumentParser = self.subparsers.add_parser(
            name="openalex",
            help="Get document metadata from OpenAlex",
            description="Step 3",
        )

        openalex_parser.add_argument(
            "-d",
            "--db",
            nargs=1,
            default=self.database_path,
            type=self._resolve_path,
            help=self.db_help,
            dest="oa.db",
        )
        openalex_parser.add_argument(
            "-e",
            "--email",
            nargs=1,
            type=str,
            help="Email address to access OpenAlex polite pool",
            required=True,
            dest="oa.email",
        )

    def add_document_filter(self) -> None:
        document_filter_parser: ArgumentParser = self.subparsers.add_parser(
            name="filter",
            help="Filter for Natural Science documents",
            description="Step 4",
        )

        document_filter_parser.add_argument(
            "-d",
            "--db",
            nargs=1,
            default=self.database_path,
            type=self._resolve_path,
            help=self.db_help,
            dest="filter.db",
        )

    def parse(self) -> Namespace:
        return self.parser.parse_args()
