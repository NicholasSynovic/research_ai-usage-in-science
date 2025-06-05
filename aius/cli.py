"""
Handle command line argument parsing.

Copyright 2025 (C) Nicholas M. Synovic

"""

from argparse import Namespace, ArgumentParser, _SubParsersAction
from pathlib import Path
import sys

COMMANDS: set[str] = {
    "init",
    "search",
    "ed",
    "oa",
    "filter",
    "aa",
    "stat",
    "download",
}


class CLI:
    def __init__(self) -> None:
        self.prog: str = "AIUS"
        self.description: str = "Identify AI usage in Natural Science research papers"
        self.epilog: str = "Copyright 2025 (C) Nicholas M. Synovic"
        self.default_database_path: Path = Path("./aius.db").resolve()

        self.parser: ArgumentParser = ArgumentParser(
            prog=self.prog,
            description=self.description,
            epilog=self.epilog,
        )

        self.subparsers: _SubParsersAction[ArgumentParser] = self.parser.add_subparsers(
            prog=self.prog
        )

        self.add_initialize_parser()
        self.add_search_parser()
        self.add_extract_documents_parser()
        self.add_openalex_parser()
        self.add_document_filter_parser()
        self.add_author_agreement_parser()
        self.add_statistics_parser()
        self.add_document_download_parser()

    def add_initialize_parser(self) -> None:
        initialize_parser: ArgumentParser = self.subparsers.add_parser(
            name="init",
            help="Initialize AIUS (Step 0)",
        )

        initialize_parser.add_argument(
            "-d",
            "--db",
            nargs=1,
            default=self.default_database_path,
            type=Path,
            help="Path to create AIUS SQLite3 database",
            dest="init.db",
        )
        initialize_parser.add_argument(
            "-f",
            "--force",
            default=False,
            action="store_true",
            help="Force creating a new database",
            dest="init.force",
        )

    def add_search_parser(self) -> None:
        search_parser: ArgumentParser = self.subparsers.add_parser(
            name="search",
            help="Search Journals (Step 1)",
        )

        search_parser.add_argument(
            "-d",
            "--db",
            nargs=1,
            default=self.default_database_path,
            type=Path,
            help="Path to AIUS SQLite3 database",
            dest="search.db",
        )
        search_parser.add_argument(
            "-j",
            "--journal",
            nargs=1,
            default="plos",
            type=str,
            choices=["nature", "plos"],
            help="Journal to search through",
            dest="search.journal",
        )

    def add_extract_documents_parser(self) -> None:
        extract_documents_parser: ArgumentParser = self.subparsers.add_parser(
            name="extract-documents",
            help="Extract Documents From Search Responses (Step 2)",
        )

        extract_documents_parser.add_argument(
            "-d",
            "--db",
            nargs=1,
            default=self.default_database_path,
            type=Path,
            help="Path to AIUS SQLite3 database",
            dest="ed.db",
        )

    def add_openalex_parser(self) -> None:
        openalex_parser: ArgumentParser = self.subparsers.add_parser(
            name="openalex",
            help="Get Document Metadata From OpenAlex (Step 3)",
        )

        openalex_parser.add_argument(
            "-d",
            "--db",
            nargs=1,
            default=self.default_database_path,
            type=Path,
            help="Path to AIUS SQLite3 database",
            dest="oa.db",
        )
        openalex_parser.add_argument(
            "-e",
            "--email",
            nargs=1,
            type=str,
            help="Email address to access OpenAlex polite pool",
            dest="oa.email",
        )

    def add_document_filter_parser(self) -> None:
        document_filter_parser: ArgumentParser = self.subparsers.add_parser(
            name="filter",
            help="Filter For Documents Relevant To This Study (Step 4)",
        )

        document_filter_parser.add_argument(
            "-d",
            "--db",
            nargs=1,
            default=self.default_database_path,
            type=Path,
            help="Path to AIUS SQLite3 database",
            dest="filter.db",
        )

    def add_author_agreement_parser(self) -> None:
        author_agreement_parser: ArgumentParser = self.subparsers.add_parser(
            name="author-agreement",
            help="Add the author agreement data to the dataset (Optional Step 5)",
        )

        author_agreement_parser.add_argument(
            "-d",
            "--db",
            nargs=1,
            default=self.default_database_path,
            type=Path,
            help="Path to AIUS SQLite3 database",
            dest="aa.db",
        )
        author_agreement_parser.add_argument(
            "-w",
            "--workbook",
            nargs=1,
            default=Path("author-agreement.xlsx"),
            type=Path,
            help="Path to author agreement Excel (.xlsx) workbook",
            dest="aa.wb",
        )

    def add_statistics_parser(self) -> None:
        statistics_parser: ArgumentParser = self.subparsers.add_parser(
            name="stat",
            help="Generate statistics and print to console (Optional Step 6)",
        )

        statistics_parser.add_argument(
            "-d",
            "--db",
            nargs=1,
            default=self.default_database_path,
            type=Path,
            help="Path to AIUS SQLite3 database",
            dest="stat.db",
        )

    def add_document_download_parser(self) -> None:
        document_download_parser: ArgumentParser = self.subparsers.add_parser(
            name="download",
            help="Download samples of PDF documents (Optional Step 7)",
        )

        document_download_parser.add_argument(
            "-d",
            "--db",
            nargs=1,
            default=self.default_database_path,
            type=Path,
            help="Path to AIUS SQLite3 database",
            dest="download.db",
        )
        document_download_parser.add_argument(
            "-s",
            "--sample",
            nargs=1,
            choices=["author-agreement", "plos-ns"],
            help="Sample of papers to download",
            dest="download.sample",
        )
        document_download_parser.add_argument(
            "-o",
            "--output-dir",
            nargs=1,
            default=Path.cwd().resolve(),
            type=Path,
            help="Path to save PDFs",
            dest="download.output",
        )

    def parse_cli(self) -> Namespace:
        return self.parser.parse_args()


def get_subparser_keyword(args: Namespace) -> str:
    argument_set: set[str] = set([arg.split(".")[0] for arg in args.__dict__.keys()])

    try:
        return list(argument_set.intersection(COMMANDS))[0]
    except IndexError as ie:
        raise ie
