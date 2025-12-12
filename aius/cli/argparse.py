"""
Argparse CLI implementation.

Copyright (C) 2025 Nicholas M. Synovic
"""

import sys
from argparse import ArgumentParser, _SubParsersAction
from datetime import datetime, timezone
from pathlib import Path

from aius.analyze import SYSTEM_PROMPT_TAG_MAPPING
from aius.cli import CLI, DATABASE_HELP_MESSAGE
from aius.db import DEFAULT_DATABASE_PATH
from aius.jats import ALL_OF_PLOS_DEFAULT_PATH
from aius.megajournals import MEGAJOURNAL_MAPPING
from aius.pandoc import DEFAULT_PANDOC_URI


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
            "--max-year",
            default=2024,
            type=lambda x: min([current_year, int(x)]),
            help="Maximum year to search journals through",
            dest="init.max",
        )

        parser.add_argument(
            "--min-year",
            default=2015,
            type=lambda x: max([1999, int(x)]),
            help="Minimum year to search journals through",
            dest="init.min",
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
            default=next(iter(MEGAJOURNAL_MAPPING.keys())),
            type=str,
            choices=list(MEGAJOURNAL_MAPPING.keys()),
            help="Journal to search for natural science documents reusing PTMs",
            dest="search.megajournal",
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

    def add_jats_subparser(self) -> None:  # noqa: D102
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
            "--megajournal",
            default=next(iter(MEGAJOURNAL_MAPPING.keys())),
            type=str,
            choices=list(MEGAJOURNAL_MAPPING.keys()),
            help="Megajournal to download JATS XML natural science works from",
            dest="jats.megajournal",
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
            "--auth-key",
            type=str,
            required=False,
            default="",
            help="Inference serve auth key (required for sophia and metis backends)",
            dest="analyze.auth_key",
        )

        parser.add_argument(
            "--backend",
            type=str,
            required=True,
            choices=["metis", "ollama", "sophia"],
            help="LLM inferencing backend",
            dest="analyze.backend",
        )

        parser.add_argument(
            "--db",
            default=DEFAULT_DATABASE_PATH,
            type=lambda x: Path(x).resolve(),
            help=DATABASE_HELP_MESSAGE,
            dest="analyze.db",
        )

        parser.add_argument(
            "--index",
            type=int,
            required=False,
            default=0,
            help="Starting index of documents. Default is 0.",
            dest="analyze.index",
        )

        parser.add_argument(
            "--max-context-tokens",
            type=int,
            required=False,
            default=100000,
            help="Maximum context tokens per document (only for ollama backend)",
            dest="analyze.max_context_tokens",
        )

        parser.add_argument(
            "--max-predict-tokens",
            type=int,
            required=False,
            default=10000,
            help="Maximum predictions tokens per response (only for ollama backend)",
            dest="analyze.max_predict_tokens",
        )

        parser.add_argument(
            "--model-name",
            required=True,
            type=str,
            help="LLM to analyze documents on",
            dest="analyze.model_name",
        )

        parser.add_argument(
            "--ollama-endpoint",
            type=str,
            required=False,
            default="http://localhost:11434",
            help="Ollama inferencing URL. Default is http://localhost:11434",
            dest="analyze.ollama_endpoint",
        )
        parser.add_argument(
            "--stride",
            type=int,
            required=False,
            default=20,
            help="Stride of documents. Default is 20",
            dest="analyze.stride",
        )

        parser.add_argument(
            "--system-prompt-id",
            default=next(iter(SYSTEM_PROMPT_TAG_MAPPING.keys())),
            type=str,
            choices=list(SYSTEM_PROMPT_TAG_MAPPING.keys()),
            help="LLM system prompt to use for analysis",
            dest="analyze.system_prompt_id",
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
