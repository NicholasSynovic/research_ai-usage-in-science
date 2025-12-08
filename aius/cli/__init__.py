from abc import ABC, abstractmethod
from importlib.metadata import version

DATABASE_HELP_MESSAGE: str = "Path to database"


class CLI(ABC):
    def __init__(self) -> None:
        self.program_name: str = "AIUS"
        self.progam_epilog: str = "Copyright 2025 (C) Nicholas M. Synovic"
        self.program_description: str = """
Empirically measure pre-trained deep learning model (PTM) reusage and its impact
in natural science publications
"""

        self.construct_cli()

    @abstractmethod
    def add_version(self) -> None: ...

    @abstractmethod
    def add_init_subparser(self) -> None: ...

    @abstractmethod
    def add_search_subparser(self) -> None: ...

    @abstractmethod
    def add_openalex_subparser(self) -> None: ...

    @abstractmethod
    def add_documents_subparser(self) -> None: ...

    @abstractmethod
    def add_pandoc_subparser(self) -> None: ...

    @abstractmethod
    def add_analyze_subparser(self) -> None: ...

    @abstractmethod
    def parse_cli(self) -> dict: ...

    @abstractmethod
    def identify_subcommand(self) -> str: ...

    @property
    def get_version(self) -> str:
        return version(distribution_name="aius")

    def construct_cli(self) -> None:
        self.add_version()
        self.add_init_subparser()
        self.add_search_subparser()
        self.add_openalex_subparser()
        self.add_documents_subparser()
        self.add_pandoc_subparser()
        self.add_analyze_subparser()
