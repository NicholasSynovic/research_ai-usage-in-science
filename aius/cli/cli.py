"""
Handle command line argument parsing file.

Copyright 2025 (C) Nicholas M. Synovic

"""

from argparse import ArgumentParser, Namespace, _SubParsersAction
import aius
from pathlib import Path


class CLI:
    def __init__(self) -> None:
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
        self.add_init()  # Initialize the application

    def add_init(self) -> None:
        initialize_parser: ArgumentParser = self.subparsers.add_parser(
            name="init",
            help=f"Initialize {aius.PROGRAM_NAME}",
            description="Step 0",
        )

        initialize_parser.add_argument(
            "-d",
            "--db",
            nargs=1,
            default=self.database_path,
            type=Path,
            help="Path to create the output database",
            dest="init.db",
        )


CLI().parser.parse_args()
