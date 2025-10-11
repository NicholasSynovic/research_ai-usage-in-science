"""
Handle command line argument parsing.

Copyright 2025 (C) Nicholas M. Synovic

"""

from argparse import ArgumentParser, Namespace, _SubParsersAction
from importlib.metadata import version
from pathlib import Path

import aius


class CLI:
    """
    CLI for interacting with the `aius` software.

    Attributes:
        db_help (str): Database path help string.
        database_path (Path): Default SQLite3 database file location within the
            program directory.
        parser (ArgumentParser): Top-level ArgumentParser instance configured
            with program name, description, and epilog.
        subparsers (_SubParsersAction[ArgumentParser]): Subparsers for
            organizing different CLI commands.

    Methods:
        add_search(): Configures and adds a search sub-parser for journals to
            find papers by keywords.
        add_identify_papers(): Configures and adds an 'identify-documents'
            sub-parser for identifying documents from journal searches.
        add_openalex(): Configures and adds an 'openalex' sub-parser for
            retrieving document metadata from OpenAlex.
        add_document_filter(): Configures and adds a 'filter' sub-parser to
            filter documents by Natural Science category.
        parse(): Parses command line arguments into Namespace objects.


    """

    def __init__(self) -> None:
        """
        Initialize the CLI.

        Initialize with common help strings, default database path,
        ArgumentParser instance, and subparsers for different commands.

        """
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
        self.add_search_plos()  # Search PLOS for papers
        self.add_identify_papers()  # Extract documents from journal search
        self.add_openalex()  # Get document metadata from OpenAlex
        self.add_document_filter()  # Filter for Natural Science documents

        # Add version argument
        self.parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=version(distribution_name=aius.MODULE_NAME),
        )

    def add_search_plos(self) -> None:
        """Add a sub-parser for searching PLOS for papers with keywords."""
        search_parser: ArgumentParser = self.subparsers.add_parser(
            name="search-plos",
            help="Search PLOS for papers",
            description="Step 1",
        )

        search_parser.add_argument(
            "-d",
            "--db",
            nargs=1,
            default=self.database_path,
            type=lambda x: Path(x).resolve(),
            help=self.db_help,
            dest="search_plos.db",
        )

    def add_identify_papers(self) -> None:
        """Add a sub-parser for identifying documents from journal searches."""
        extract_documents_parser: ArgumentParser = self.subparsers.add_parser(
            name="identify-documents",
            help="Identify documents from journal searches",
            description="Step 2",
        )

        extract_documents_parser.add_argument(
            "-d",
            "--db",
            nargs=1,
            default=self.database_path,
            type=lambda x: Path(x).resolve(),
            help=self.db_help,
            dest="identify_documents.db",
        )

    def add_openalex(self) -> None:
        """Configure a sub-parser for retrieving metadata from OpenAlex."""
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
            type=lambda x: Path(x).resolve(),
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
        """Add a sub-parser to filter documents by Natural Science category."""
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
            type=lambda x: Path(x).resolve(),
            help=self.db_help,
            dest="filter.db",
        )

    @property
    def parse(self) -> dict:
        """
        Parse and return command-line arguments as a `dict` object.

        This method encapsulates the parsing of command-line inputs into
        structured data, enabling access to specific options and their values
        through attributes derived from the parsed arguments. It serves as an
        entry point for accessing detailed information about user commands,
        facilitating further processing within the CLI framework.

        Returns:
            dict: An object containing all parsed command-line arguments,
                allowing developers to easily reference and utilize these inputs
                in subsequent operations.

        """
        return self.parser.parse_args().__dict__
