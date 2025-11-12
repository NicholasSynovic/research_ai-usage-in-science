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

        # # Queries PLOS
        # self.add_search_plos()

        # # Organizes data; all commands related to papers come after this one
        # self.add_identify_papers()

        # # These load CSV files that reference papers by DOI
        # self.add_load_pilot_study()
        # self.add_load_author_agreement()
        # self.add_load_llm_prompt_engineering_papers()

        # # Query OpenAlex
        # self.add_openalex()

        # # Identify Natural Science documents
        # self.add_document_filter()

        # # Load data from all_of_plos.zip and `pandoc`
        # self.add_content_retriever()

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
            nargs=1,
            default=self.database_path,
            type=lambda x: Path(x).resolve(),
            help=DB_HELP_MESSAGE,
            dest="init.db",
        )

        parser.add_argument(
            "--min-year",
            nargs=1,
            default=2015,
            type=lambda x: max([2000, x]),
            help=MIN_YEAR_HELP,
            dest="init.min",
        )

        parser.add_argument(
            "--max-year",
            nargs=1,
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
            nargs=1,
            default=self.database_path,
            type=lambda x: Path(x).resolve(),
            help=DB_HELP_MESSAGE,
            dest="search.db",
        )

        parser.add_argument(
            "--journal",
            nargs=1,
            default=JOURNAL_CHOICES[0],
            type=str,
            choices=JOURNAL_CHOICES,
            help=JOURNAL_HELP,
            dest="search.journal",
        )

    # def add_search_plos(self) -> None:
    #     """Add a sub-parser for searching PLOS for papers with keywords."""
    #     search_parser: ArgumentParser = self.subparsers.add_parser(
    #         name="search-plos",
    #         help="Search PLOS for papers",
    #         description="Step 1",
    #     )

    #     search_parser.add_argument(
    #         "-d",
    #         "--db",
    #         nargs=1,
    #         default=self.database_path,
    #         type=lambda x: Path(x).resolve(),
    #         help=self.db_help,
    #         dest="search_plos.db",
    #     )

    # def add_identify_papers(self) -> None:
    #     """Add a sub-parser for identifying documents from journal searches."""
    #     extract_documents_parser: ArgumentParser = self.subparsers.add_parser(
    #         name="identify-documents",
    #         help="Identify documents from journal searches",
    #         description="Step 2",
    #     )

    #     extract_documents_parser.add_argument(
    #         "-d",
    #         "--db",
    #         nargs=1,
    #         default=self.database_path,
    #         type=lambda x: Path(x).resolve(),
    #         help=self.db_help,
    #         dest="identify_documents.db",
    #     )

    # def add_load_pilot_study(self) -> None:
    #     """Add a sub-parser to retrieve PLOS Natural Science paper content."""
    #     load_pilot_study_parser: ArgumentParser = self.subparsers.add_parser(
    #         name="load-pilot-study",
    #         help="Load pilot study dataset",
    #         description="Step 3",
    #     )

    #     load_pilot_study_parser.add_argument(
    #         "-d",
    #         "--db",
    #         nargs=1,
    #         default=self.database_path,
    #         type=lambda x: Path(x).resolve(),
    #         help=self.db_help,
    #         dest="load_pilot_study.db",
    #     )
    #     load_pilot_study_parser.add_argument(
    #         "-i",
    #         "--input-fp",
    #         nargs=1,
    #         required=True,
    #         type=lambda x: Path(x).resolve(),
    #         help="Path to pilot study CSV file",
    #         dest="load_pilot_study.fp",
    #     )

    # def add_load_author_agreement(self) -> None:
    #     author_agreement_parser: ArgumentParser = self.subparsers.add_parser(
    #         name="load-author-agreement",
    #         help="Load author agreement dataset",
    #         description="Step 4",
    #     )

    #     author_agreement_parser.add_argument(
    #         "-d",
    #         "--db",
    #         nargs=1,
    #         default=self.database_path,
    #         type=lambda x: Path(x).resolve(),
    #         help=self.db_help,
    #         dest="load_author_agreement.db",
    #     )
    #     author_agreement_parser.add_argument(
    #         "-i",
    #         "--input-fp",
    #         nargs=1,
    #         required=True,
    #         type=lambda x: Path(x).resolve(),
    #         help="Path to author agreement CSV file",
    #         dest="load_author_agreement.fp",
    #     )

    # def add_load_llm_prompt_engineering_papers(self) -> None:
    #     llm_prompt_engineering_papers_parser: ArgumentParser = (
    #         self.subparsers.add_parser(
    #             name="load-llm-prompt-engineering-papers",
    #             help="Load LLM prompt engineering papers into the database",
    #             description="Step 5",
    #         )
    #     )

    #     llm_prompt_engineering_papers_parser.add_argument(
    #         "-d",
    #         "--db",
    #         nargs=1,
    #         default=self.database_path,
    #         type=lambda x: Path(x).resolve(),
    #         help=self.db_help,
    #         dest="load_llm_prompt_prompt_engineering_papers.db",
    #     )

    # def add_openalex(self) -> None:
    #     """Configure a sub-parser for retrieving metadata from OpenAlex."""
    #     openalex_parser: ArgumentParser = self.subparsers.add_parser(
    #         name="openalex",
    #         help="Get document metadata from OpenAlex",
    #         description="Step 6",
    #     )

    #     openalex_parser.add_argument(
    #         "-d",
    #         "--db",
    #         nargs=1,
    #         default=self.database_path,
    #         type=lambda x: Path(x).resolve(),
    #         help=self.db_help,
    #         dest="openalex.db",
    #     )
    #     openalex_parser.add_argument(
    #         "-e",
    #         "--email",
    #         nargs=1,
    #         type=str,
    #         help="Email address to access OpenAlex polite pool",
    #         required=True,
    #         dest="openalex.email",
    #     )

    # def add_document_filter(self) -> None:
    #     """Add a sub-parser to filter documents by Natural Science category."""
    #     document_filter_parser: ArgumentParser = self.subparsers.add_parser(
    #         name="filter-documents",
    #         help="Filter for Natural Science documents",
    #         description="Step 7",
    #     )

    #     document_filter_parser.add_argument(
    #         "-d",
    #         "--db",
    #         nargs=1,
    #         default=self.database_path,
    #         type=lambda x: Path(x).resolve(),
    #         help=self.db_help,
    #         dest="doucment_filter.db",
    #     )

    # def add_content_retriever(self) -> None:
    #     """Add a sub-parser to retrieve PLOS Natural Science paper content."""
    #     content_retriever_parser: ArgumentParser = self.subparsers.add_parser(
    #         name="retrieve-content",
    #         help="Retrieve content from PLOS Natural Science documents",
    #         description="Step 8",
    #     )

    #     content_retriever_parser.add_argument(
    #         "-d",
    #         "--db",
    #         nargs=1,
    #         default=self.database_path,
    #         type=lambda x: Path(x).resolve(),
    #         help=self.db_help,
    #         dest="content_retriever.db",
    #     )
    #     content_retriever_parser.add_argument(
    #         "-i",
    #         "--input-fp",
    #         nargs=1,
    #         required=True,
    #         type=lambda x: Path(x).resolve(),
    #         help="Path to All of PLOS zip file",
    #         dest="content_retriever.fp",
    #     )
    #     content_retriever_parser.add_argument(
    #         "-p",
    #         "--pandoc-url",
    #         nargs=1,
    #         type=str,
    #         default=["http://localhost:3030"],
    #         help="Pandoc server URL",
    #         dest="content_retriever.pandoc_url",
    #     )

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
