"""
Main executable file.

Copyright 2025 (C) Nicholas M. Synovic

"""

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from aius import MODULE_NAME
from aius.cli.argparse import Argparse
from aius.factory import Runner, runner_factory


def setup_logging() -> None:  # noqa: D103
    # Get the current timestamp
    timestamp: int = int(datetime.now(tz=timezone.utc).timestamp())

    # Log file
    log_file: Path = Path(f"{MODULE_NAME}_{timestamp}.log").resolve()

    # Setup the logger
    logging.getLogger()
    logging.basicConfig(
        filename=log_file,
        filemode="w",
        encoding="UTF-8",
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s:%(message)s",
    )


def main() -> int:  # noqa: D103
    setup_logging()
    logger = logging.getLogger()
    logger.info(msg="Hello world!")

    # Run the command line interface
    cli: Argparse = Argparse()
    args: dict = cli.parse_cli()
    logger.debug("Command line input: %s", args)

    # Get the appropriate runner method
    subparser: str = cli.identify_subcommand()
    logger.debug("Subparser: %s", subparser)

    # This function identifies which runner to execute, and then moves the code
    # over to aius/runners/__init__.py for further execution
    runner: Runner | int = runner_factory(
        logger=logger,
        runner_name=subparser,
        **args,
    )

    if isinstance(runner, int):
        return 1

    runner_status: int = runner.execute()

    if runner_status == 1:
        logger.error("Unable to get the proper subparser runner: %s", subparser)
        sys.exit(1)

    return 0


if __name__ == "__main__":
    main()
