from logging import Logger
from pathlib import Path

from aius.db import DB
from aius.runners.init import InitRunner
from aius.runners.jats import JATSRunner
from aius.runners.openalex import OpenAlexRunner
from aius.runners.search import SearchRunner


def connect_to_db(logger: Logger, db_path: Path) -> DB:
    logger.info(msg=f"Connected to SQLite3 database: {db_path}")
    return DB(logger=logger, db_path=db_path)


def init(logger: Logger, **kwargs) -> None:
    logger.debug(msg=f"init kwargs: {kwargs}")

    # Connect to the database
    db: DB = connect_to_db(logger=logger, db_path=kwargs["init.db"])

    # Execute runner
    runner: InitRunner = InitRunner(
        db=db,
        min_year=kwargs["init.min"],
        max_year=kwargs["init.max"],
        logger=logger,
    )
    runner.execute()


def search(logger: Logger, **kwargs) -> None:
    logger.debug(msg=f"search kwargs: {kwargs}")

    # Connect to the database
    db: DB = connect_to_db(logger=logger, db_path=kwargs["search.db"])

    # Execute runner
    runner: SearchRunner = SearchRunner(
        logger=logger,
        db=db,
        journal=kwargs["search.journal"],
    )
    runner.execute()


def openalex(logger: Logger, **kwargs) -> None:
    logger.debug(msg=f"openalex kwargs: {kwargs}")

    # Connect to the database
    db: DB = connect_to_db(logger=logger, db_path=kwargs["openalex.db"])

    # Execute runner
    runner: OpenAlexRunner = OpenAlexRunner(
        logger=logger,
        db=db,
        email=kwargs["openalex.email"],
    )
    runner.execute()


def jats(logger: Logger, **kwargs) -> None:
    logger.debug(msg=f"jats kwargs: {kwargs}")

    # Connect to the database
    db: DB = connect_to_db(logger=logger, db_path=kwargs["jats.db"])

    # Execute runner
    runner: JATSRunner = JATSRunner(
        logger=logger,
        db=db,
        plos_zip_fp=kwargs["jats.plos_zip"],
    )
    runner.execute()
