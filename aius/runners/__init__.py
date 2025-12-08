"""
Entrypoint for runners.

Copyright 2025 (C) Nicholas M. Synovic

"""

from abc import ABC, abstractmethod
from logging import Logger
from pathlib import Path

from aius.db import DB
from aius.runners.analysis import AnalysisRunner
from aius.runners.init import InitRunner
from aius.runners.jats import JATSRunner
from aius.runners.openalex import OpenAlexRunner
from aius.runners.pandoc import PandocRunner
from aius.runners.search import SearchRunner


class Runner(ABC):  # noqa: D101
    def __init__(self, name: str, db: DB) -> None:  # noqa: D107
        self.name: str = name
        self.db: DB = db

    @abstractmethod
    def execute(self) -> int: ...  # noqa: D102


def connect_to_db(logger: Logger, db_path: Path) -> DB:  # noqa: D103
    logger.info("Connected to SQLite3 database: %s", db_path)
    return DB(logger=logger, db_path=db_path)


def handle_runner(logger: Logger, runner_name: str, **kwargs) -> int:  # noqa: ANN003, D103
    logger.info("%s kwargs: %s", runner_name, kwargs)

    # Connect to the database
    db: DB = connect_to_db(logger=logger, db_path=kwargs[f"{runner_name}.db"])

    match runner_name:
        case "init":
            runner = InitRunner(
                db=db,
                min_year=kwargs["init.min"],
                max_year=kwargs["init.max"],
                logger=logger,
            )
        case "search":
            runner = SearchRunner(
                logger=logger,
                db=db,
                journal=kwargs["search.journal"],
            )
        case "openalex":
            runner = OpenAlexRunner(
                logger=logger,
                db=db,
                email=kwargs["openalex.email"],
            )
        case "jats":
            runner = JATSRunner(
                logger=logger,
                db=db,
                plos_zip_fp=kwargs["jats.plos_zip"],
            )
        case "pandoc":
            runner = PandocRunner(
                logger=logger,
                db=db,
                pandoc_uri=kwargs["pandoc.uri"],
            )
        case "analysis":
            runner = AnalysisRunner(
                logger=logger,
                db=db,
                prompt_id=kwargs["analysis.prompt"],
                alcf_auth_token=kwargs["analysis.auth"],
            )
        case _:
            return 1

    return runner.execute()
