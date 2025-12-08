import logging
import sys
from datetime import datetime, timezone
from logging import Logger
from pathlib import Path

from aius import MODULE_NAME, runners
from aius.cli.argparse import Argparse


def setup_logging() -> None:
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


def get_subparser_runner(subparser: str):
    match subparser:
        case "init":
            return runners.init
        case "search":
            return runners.search
        case "openalex":
            return runners.openalex
        case "jats":
            return runners.jats
        case "pandoc":
            return runners.pandoc
        case "analysis":
            return runners.analysis
        case _:
            return -1


def main() -> int:
    setup_logging()
    logger = logging.getLogger()
    logger.info(msg="Hello world!")

    # Run the command line interface
    cli: Argparse = Argparse()
    args: dict = cli.parse_cli()
    logger.debug(msg=f"Command line input: {args}")

    # Get the appropriate runner method
    subparser: str = cli.identify_subcommand()
    logger.debug(msg=f"Subparser: {subparser}")
    runner = get_subparser_runner(subparser=subparser)

    # Handle invalid runners
    if runner == -1:
        logger.error(
            msg=f"Unable to get the proper subparser runner: {subparser}",
        )
        sys.exit(1)

    # Run code
    runner(logger=logger, **args)

    return 0


if __name__ == "__main__":
    main()
