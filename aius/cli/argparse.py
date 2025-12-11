"""
Argparse CLI implementation.

Copyright (C) 2025 Nicholas M. Synovic
"""

import sys
from argparse import ArgumentParser, _SubParsersAction
from datetime import datetime, timezone
from pathlib import Path

from aius.cli import CLI, DATABASE_HELP_MESSAGE
from aius.db import DEFAULT_DATABASE_PATH
from aius.documents import ALL_OF_PLOS_DEFAULT_PATH
from aius.inference import SYSTEM_PROMPT_TAG_MAPPING
from aius.pandoc import DEFAULT_PANDOC_URI
from aius.search import JOURNAL_SEARCH_MAPPING


class Argparse(CLI):  # noqa: D101
    def __init__(self) -> None:  # noqa: D107
        super().__init__()

        self.parser: ArgumentParser = ArgumentParser(
            prog=self.program_name,
            description=self.program_description,
            epilog=self.progam_epilog,
        )

        self.subparsers: _SubParsersAction[ArgumentParser] = self.parser.add_subparsers(
            prog=self.program_name
        )

        self.construct_cli()

    def add_version(self) -> None:  # noqa: D102
        self.parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=self.get_version,
        )

    def add_init_subparser(self) -> None:  # noqa: D102
        current_year: int = datetime.now(tz=timezone.utc).year

        parser: ArgumentParser = self.subparsers.add_parser(
            name="init",
            help="Initialize the database",
            description="Step 0",
        )

        parser.add_argument(
            "--db",
            default=parser,
            type=lambda x: Path(x).resolve(),
            help=DATABASE_HELP_MESSAGE,
            dest="init.db",
        )

        parser.add_argument(
            "--min-year",
            default=2015,
            type=lambda x: max([1999, int(x)]),
            help="Minimum year to search journals through",
            dest="init.min",
        )

        parser.add_argument(
            "--max-year",
            default=2024,
            type=lambda x: min([current_year, int(x)]),
            help="Maximum year to search journals through",
            dest="init.max",
        )

    def add_search_subparser(self) -> None:  # noqa: D102
        parser: ArgumentParser = self.subparsers.add_parser(
            name="search",
            help="Search Journals",
            description="Step 1",
        )

        parser.add_argument(
            "--db",
            default=DEFAULT_DATABASE_PATH,
            type=lambda x: Path(x).resolve(),
            help=DATABASE_HELP_MESSAGE,
            dest="search.db",
        )

        parser.add_argument(
            "--journal",
            default=next(iter(JOURNAL_SEARCH_MAPPING.keys())),
            type=str,
            choices=list(JOURNAL_SEARCH_MAPPING.keys()),
            help="Journal to search for natural science documents reusing PTMs",
            dest="search.journal",
        )

    def add_openalex_subparser(self) -> None:  # noqa: D102
        parser: ArgumentParser = self.subparsers.add_parser(
            name="openalex",
            help="Get document metadata from OpenAlex academic indexer",
            description="Step 2",
        )

        parser.add_argument(
            "--db",
            default=DEFAULT_DATABASE_PATH,
            type=lambda x: Path(x).resolve(),
            help=DATABASE_HELP_MESSAGE,
            dest="openalex.db",
        )

        parser.add_argument(
            "--email",
            type=str,
            help="Email address to access OpenAlex polite pool",
            required=True,
            dest="openalex.email",
        )

    def add_documents_subparser(self) -> None:  # noqa: D102
        parser: ArgumentParser = self.subparsers.add_parser(
            name="jats",
            help="Get JATS XML from DOIs",
            description="Step 3",
        )

        parser.add_argument(
            "--db",
            default=DEFAULT_DATABASE_PATH,
            type=lambda x: Path(x).resolve(),
            help=DATABASE_HELP_MESSAGE,
            dest="jats.db",
        )
        parser.add_argument(
            "--plos-zip",
            default=ALL_OF_PLOS_DEFAULT_PATH,
            type=lambda x: Path(x).resolve(),
            help="Path to PLOS ZIP file containing all PLOS documents",
            dest="jats.plos_zip",
        )

    def add_pandoc_subparser(self) -> None:  # noqa: D102
        pandoc_parser: ArgumentParser = self.subparsers.add_parser(
            name="pandoc",
            help="Convert documents to Markdown with Pandoc",
            description="Step 4",
        )

        pandoc_parser.add_argument(
            "--db",
            default=DEFAULT_DATABASE_PATH,
            type=lambda x: Path(x).resolve(),
            help=DATABASE_HELP_MESSAGE,
            dest="pandoc.db",
        )

        pandoc_parser.add_argument(
            "--uri",
            default=DEFAULT_PANDOC_URI,
            type=str,
            help="URI to pandoc server instance",
            dest="pandoc.uri",
        )

    def add_analyze_subparser(self) -> None:  # noqa: D102
        parser: ArgumentParser = self.subparsers.add_parser(
            name="analyze",
            help="Analyze documents with LLMs for PTM reuse patterns",
            description="Step 5",
        )

        parser.add_argument(
            "--db",
            default=DEFAULT_DATABASE_PATH,
            type=lambda x: Path(x).resolve(),
            help=DATABASE_HELP_MESSAGE,
            dest="analyze.db",
        )

        parser.add_argument(
            "--system-prompt",
            default=next(iter(SYSTEM_PROMPT_TAG_MAPPING.keys())),
            type=str,
            choices=list(SYSTEM_PROMPT_TAG_MAPPING.keys()),
            help="LLM system prompt to use for analysis",
            dest="analyze.system_prompt",
        )

        parser.add_argument(
            "--auth-key",
            type=str,
            required=True,
            help="ALCF Inference server token",
            dest="analyze.auth",
        )

        parser.add_argument(
            "--index",
            type=int,
            required=False,
            default=0,
            help="Starting index of documents",
            dest="analyze.index",
        )

        parser.add_argument(
            "--stride",
            type=int,
            required=False,
            default=20,
            help="Stride of documents",
            dest="analyze.stride",
        )

        parser.add_argument(
            "--backend",
            type=str,
            required=True,
            choices=["alcf", "ollama"],
            help="AI inferencing backend",
            dest="analyze.backend",
        )

        parser.add_argument(
            "--ollama",
            type=str,
            required=False,
            default="http://localhost:11434/v1",
            help="OpenAI inferencing URL",
            dest="analyze.ollama",
        )

    def parse_cli(self) -> dict:  # noqa: D102
        return self.parser.parse_args().__dict__

    def identify_subcommand(self) -> str:  # noqa: D102
        args: dict = self.parse_cli()
        arg_keys: list[str] = list(args.keys())
        try:
            return arg_keys[0].split(sep=".")[0]
        except IndexError:
            print("Help command: aius [-h] [--help]")
            sys.exit(1)
