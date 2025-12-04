from argparse import ArgumentParser, _SubParsersAction
from datetime import datetime
from importlib.metadata import version
from pathlib import Path

from aius import MODULE_NAME
from aius.cli import *


class CLI:
    def __init__(self) -> None:
        # Get the current year for comparison
        self.current_year: int = datetime.now().year

        # Set CLI default values
        self.database_path: Path = DB_DEFAULT_PATH

        # Instantiate top-level and sub-parsers
        self.parser: ArgumentParser = ArgumentParser(
            prog=PROGRAM_NAME,
            description=PROGRAM_DESCRIPTION,
            epilog=PROGRAM_EPILOG,
        )
        self.subparsers: _SubParsersAction[ArgumentParser] = self.parser.add_subparsers(
            prog=PROGRAM_NAME,
        )

        # Step 0: Load constants into the database
        self.add_load_constants()

        # Step 1: Search
        self.add_search()

        # Step 2: Search OpenAlex
        self.add_openalex()

        # Step 3: Get JATS XML content from Natural Science DOIs
        self.add_jats()

        # Step 4: Convert JATS XML to Markdown and compute rough token counts
        self.add_pandoc()

        # # Add analysis
        # self.add_llm_prompt_engineering()
        # self.add_run_llm_uses_dl_analysis()
        # self.add_run_llm_uses_ptms_analysis()
        # self.add_run_llm_identify_ptms_analysis()
        # self.add_run_llm_identify_reuse_analysis()

        # Add version argument
        self.parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=version(distribution_name=MODULE_NAME),
        )

    def add_load_constants(self) -> None:
        parser: ArgumentParser = self.subparsers.add_parser(
            name="init",
            help="Initialize the database",
            description="Step 0",
        )

        parser.add_argument(
            "--db",
            default=self.database_path,
            type=lambda x: Path(x).resolve(),
            help=DB_HELP_MESSAGE,
            dest="init.db",
        )

        parser.add_argument(
            "--min-year",
            default=2015,
            type=lambda x: max([2000, x]),
            help=MIN_YEAR_HELP,
            dest="init.min",
        )

        parser.add_argument(
            "--max-year",
            default=2024,
            type=lambda x: min([self.current_year, x]),
            help=MAX_YEAR_HELP,
            dest="init.max",
        )

    def add_search(self) -> None:
        parser: ArgumentParser = self.subparsers.add_parser(
            name="search",
            help="Search Journals",
            description="Step 1",
        )

        parser.add_argument(
            "--db",
            default=self.database_path,
            type=lambda x: Path(x).resolve(),
            help=DB_HELP_MESSAGE,
            dest="search.db",
        )

        parser.add_argument(
            "--journal",
            default=JOURNAL_CHOICES[0],
            type=str,
            choices=JOURNAL_CHOICES,
            help=JOURNAL_HELP,
            dest="search.journal",
        )

    def add_openalex(self) -> None:
        """Configure a sub-parser for retrieving metadata from OpenAlex."""
        openalex_parser: ArgumentParser = self.subparsers.add_parser(
            name="openalex",
            help="Get document metadata from OpenAlex",
            description="Step 2",
        )

        openalex_parser.add_argument(
            "--db",
            default=self.database_path,
            type=lambda x: Path(x).resolve(),
            help=DB_HELP_MESSAGE,
            dest="openalex.db",
        )
        openalex_parser.add_argument(
            "--email",
            type=str,
            help="Email address to access OpenAlex polite pool",
            required=True,
            dest="openalex.email",
        )

    def add_jats(self) -> None:
        """Configure a sub-parser for getting JATS XML from DOIs."""
        jats_parser: ArgumentParser = self.subparsers.add_parser(
            name="jats",
            help="Get JATS XML from DOIs",
            description="Step 3",
        )

        jats_parser.add_argument(
            "--db",
            default=self.database_path,
            type=lambda x: Path(x).resolve(),
            help=DB_HELP_MESSAGE,
            dest="jats.db",
        )
        jats_parser.add_argument(
            "--plos-zip",
            default=self.database_path,
            type=lambda x: Path(x).resolve(),
            help="Path to PLOS ZIP file containing all PLOS documents",
            dest="jats.plos_zip",
        )

    def add_pandoc(self) -> None:
        """Configure a sub-parser for converting JATS XML to Markdown."""
        pandoc_parser: ArgumentParser = self.subparsers.add_parser(
            name="pandoc",
            help="Convert JATS XML to Markdown with Pandoc",
            description="Step 4",
        )

        pandoc_parser.add_argument(
            "--db",
            default=self.database_path,
            type=lambda x: Path(x).resolve(),
            help=DB_HELP_MESSAGE,
            dest="pandoc.db",
        )

        pandoc_parser.add_argument(
            "--uri",
            default="http://localhost:3030",
            type=str,
            help="URI to pandoc server instance",
            dest="pandoc.uri",
        )

    # def add_llm_prompt_engineering(self) -> None:
    #     llm_prompt_engineering_parser: ArgumentParser = self.subparsers.add_parser(
    #         name="llm-prompt-engineering",
    #         help="Run LLM prompt engineering analysis",
    #         description="Step 9",
    #     )

    #     llm_prompt_engineering_parser.add_argument(
    #         "-d",
    #         "--db",
    #         nargs=1,
    #         default=self.database_path,
    #         type=lambda x: Path(x).resolve(),
    #         help=self.db_help,
    #         dest="run_llm_prompt_engineering.db",
    #     )

    #     llm_prompt_engineering_parser.add_argument(
    #         "-m",
    #         "--model",
    #         type=str,
    #         required=True,
    #         choices=[
    #             "gpt-oss:20b",
    #             "magistral:24b",
    #             "qwen3:32b",
    #             "deepseek-r1:70b",
    #         ],
    #         help="LLM to run prompt engineering analysis on",
    #         dest="run_llm_prompt_engineering.model",
    #     )

    #     llm_prompt_engineering_parser.add_argument(
    #         "-p",
    #         "--prompt",
    #         type=str,
    #         required=True,
    #         choices=[
    #             "uses_dl",
    #             "uses_ptms",
    #             "identify_ptms",
    #             "identify_reuse",
    #             "identify_science",
    #         ],
    #         help="Prompt to use",
    #         dest="run_llm_prompt_engineering.prompt",
    #     )

    #     llm_prompt_engineering_parser.add_argument(
    #         "--ollama",
    #         nargs=1,
    #         type=str,
    #         required=True,
    #         help="Ollama URI",
    #         dest="run_llm_prompt_engineering.ollama",
    #     )

    #     llm_prompt_engineering_parser.add_argument(
    #         "--dataset-size",
    #         type=str,
    #         required=True,
    #         choices=["small", "large"],
    #         help="Dataset size to run prompt engineering on",
    #         dest="run_llm_prompt_engineering.dataset_size",
    #     )

    # def add_run_llm_uses_dl_analysis(self) -> None:
    #     llm_uses_dl_analysis: ArgumentParser = self.subparsers.add_parser(
    #         name="llm-analysis-uses-dl",
    #         help="Run LLM uses PTMS analysis",
    #         description="Step 11",
    #     )

    #     llm_uses_dl_analysis.add_argument(
    #         "-d",
    #         "--db",
    #         nargs=1,
    #         default=self.database_path,
    #         type=lambda x: Path(x).resolve(),
    #         help=self.db_help,
    #         dest="run_llm_uses_dl_analysis.db",
    #     )

    #     llm_uses_dl_analysis.add_argument(
    #         "-m",
    #         "--model",
    #         type=str,
    #         required=True,
    #         choices=["phi3:14b", "gpt-oss:20b", "magistral:24b"],
    #         help="LLM to run prompt engineering analysis on",
    #         dest="run_llm_uses_dl_analysis.model",
    #     )

    #     llm_uses_dl_analysis.add_argument(
    #         "--ollama",
    #         nargs=1,
    #         type=str,
    #         required=True,
    #         help="Ollama URI",
    #         dest="run_llm_uses_dl_analysis.ollama",
    #     )

    #     llm_uses_dl_analysis.add_argument(
    #         "--index",
    #         nargs=1,
    #         type=int,
    #         default=[0],
    #         help="Starting index of the dataset used for processing a subset of the dataset",
    #         dest="run_llm_uses_dl_analysis.index",
    #     )

    #     llm_uses_dl_analysis.add_argument(
    #         "--stride",
    #         nargs=1,
    #         type=int,
    #         default=[1],
    #         help="Step value to iterate through the dataset",
    #         dest="run_llm_uses_dl_analysis.stride",
    #     )

    # def add_run_llm_uses_ptms_analysis(self) -> None:
    #     llm_uses_ptms_analysis: ArgumentParser = self.subparsers.add_parser(
    #         name="llm-analysis-uses-ptms",
    #         help="Run LLM uses PTMs analysis",
    #         description="Step 12",
    #     )

    #     llm_uses_ptms_analysis.add_argument(
    #         "-d",
    #         "--db",
    #         nargs=1,
    #         default=self.database_path,
    #         type=lambda x: Path(x).resolve(),
    #         help=self.db_help,
    #         dest="run_llm_uses_ptms_analysis.db",
    #     )

    #     llm_uses_ptms_analysis.add_argument(
    #         "-m",
    #         "--model",
    #         type=str,
    #         required=True,
    #         choices=["phi3:14b", "gpt-oss:20b", "magistral:24b"],
    #         help="LLM to run prompt engineering analysis on",
    #         dest="run_llm_uses_ptms_analysis.model",
    #     )

    #     llm_uses_ptms_analysis.add_argument(
    #         "--ollama",
    #         nargs=1,
    #         type=str,
    #         required=True,
    #         help="Ollama URI",
    #         dest="run_llm_uses_ptms_analysis.ollama",
    #     )

    #     llm_uses_ptms_analysis.add_argument(
    #         "--index",
    #         nargs=1,
    #         type=int,
    #         default=[0],
    #         help="Starting index of the dataset used for processing a subset of the dataset",
    #         dest="run_llm_uses_ptms_analysis.index",
    #     )

    #     llm_uses_ptms_analysis.add_argument(
    #         "--stride",
    #         nargs=1,
    #         type=int,
    #         default=[1],
    #         help="Step value to iterate through the dataset",
    #         dest="run_llm_uses_ptms_analysis.stride",
    #     )

    #     llm_uses_ptms_analysis.add_argument(
    #         "--input-fp",
    #         nargs=1,
    #         required=True,
    #         type=lambda x: Path(x).resolve(),
    #         help="Path to uses_dl results for the spcific model",
    #         dest="run_llm_uses_ptms_analysis.input_fp",
    #     )

    # def add_run_llm_identify_ptms_analysis(self) -> None:
    #     llm_identify_ptms_analysis: ArgumentParser = self.subparsers.add_parser(
    #         name="llm-analysis-identify-ptms",
    #         help="Run LLM identify PTMs analysis",
    #         description="Step 13",
    #     )

    #     llm_identify_ptms_analysis.add_argument(
    #         "-d",
    #         "--db",
    #         nargs=1,
    #         default=self.database_path,
    #         type=lambda x: Path(x).resolve(),
    #         help=self.db_help,
    #         dest="run_llm_identify_ptms_analysis.db",
    #     )

    #     llm_identify_ptms_analysis.add_argument(
    #         "-m",
    #         "--model",
    #         type=str,
    #         required=True,
    #         choices=["phi3:14b", "gpt-oss:20b", "magistral:24b"],
    #         help="LLM to run prompt engineering analysis on",
    #         dest="run_llm_identify_ptms_analysis.model",
    #     )

    #     llm_identify_ptms_analysis.add_argument(
    #         "--ollama",
    #         nargs=1,
    #         type=str,
    #         required=True,
    #         help="Ollama URI",
    #         dest="run_llm_identify_ptms_analysis.ollama",
    #     )

    #     llm_identify_ptms_analysis.add_argument(
    #         "--index",
    #         nargs=1,
    #         type=int,
    #         default=[0],
    #         help="Starting index of the dataset used for processing a subset of the dataset",
    #         dest="run_llm_identify_ptms_analysis.index",
    #     )

    #     llm_identify_ptms_analysis.add_argument(
    #         "--stride",
    #         nargs=1,
    #         type=int,
    #         default=[1],
    #         help="Step value to iterate through the dataset",
    #         dest="run_llm_identify_ptms_analysis.stride",
    #     )

    #     llm_identify_ptms_analysis.add_argument(
    #         "--uses-ptms",
    #         nargs=1,
    #         required=True,
    #         type=lambda x: Path(x).resolve(),
    #         help="Path to uses_ptms results for the spcific model",
    #         dest="run_llm_identify_ptms_analysis.uses_ptms",
    #     )

    # def add_run_llm_identify_reuse_analysis(self) -> None:
    #     llm_identify_reuse_analysis: ArgumentParser = self.subparsers.add_parser(
    #         name="llm-analysis-identify-reuse",
    #         help="Run LLM identify reuse analysis",
    #         description="Step 14",
    #     )

    #     llm_identify_reuse_analysis.add_argument(
    #         "-d",
    #         "--db",
    #         nargs=1,
    #         default=self.database_path,
    #         type=lambda x: Path(x).resolve(),
    #         help=self.db_help,
    #         dest="run_llm_identify_reuse_analysis.db",
    #     )

    #     llm_identify_reuse_analysis.add_argument(
    #         "-m",
    #         "--model",
    #         type=str,
    #         required=True,
    #         choices=["phi3:14b", "gpt-oss:20b", "magistral:24b"],
    #         help="LLM to run prompt engineering analysis on",
    #         dest="run_llm_identify_reuse_analysis.model",
    #     )

    #     llm_identify_reuse_analysis.add_argument(
    #         "--ollama",
    #         nargs=1,
    #         type=str,
    #         required=True,
    #         help="Ollama URI",
    #         dest="run_llm_identify_reuse_analysis.ollama",
    #     )

    #     llm_identify_reuse_analysis.add_argument(
    #         "--index",
    #         nargs=1,
    #         type=int,
    #         default=[0],
    #         help="Starting index of the dataset used for processing a subset of the dataset",
    #         dest="run_llm_identify_reuse_analysis.index",
    #     )

    #     llm_identify_reuse_analysis.add_argument(
    #         "--stride",
    #         nargs=1,
    #         type=int,
    #         default=[1],
    #         help="Step value to iterate through the dataset",
    #         dest="run_llm_identify_reuse_analysis.stride",
    #     )

    #     llm_identify_reuse_analysis.add_argument(
    #         "--uses-ptms",
    #         nargs=1,
    #         required=True,
    #         type=lambda x: Path(x).resolve(),
    #         help="Path to uses_ptms results for the spcific model",
    #         dest="run_llm_identify_reuse_analysis.uses_ptms",
    #     )

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

    @property
    def identify_subparser(self) -> str:
        args: dict = self.parse
        arg_keys: list[str] = list(args.keys())
        return arg_keys[0].split(sep=".")[0]
