"""
Entrypoint for runners.

Copyright 2025 (C) Nicholas M. Synovic

"""

from logging import Logger
from pathlib import Path

from aius.db import DB
from aius.init import InitRunner
from aius.runners.analysis import AnalysisRunner
from aius.runners.jats import JATSRunner
from aius.runners.openalex import OpenAlexRunner
from aius.runners.pandoc import PandocRunner
from aius.runners.search import SearchRunner


def connect_to_db(logger: Logger, db_path: Path) -> DB:  # noqa: D103
    logger.info("Connected to SQLite3 database: %s", db_path)
    return DB(logger=logger, db_path=db_path)


# Factory method design pattern implementation
def runner_factory(logger: Logger, runner_name: str, **kwargs) -> int:  # noqa: ANN003, D103
    logger.info("%s kwargs: %s", runner_name, kwargs)

    # Connect to the database
    db: DB = connect_to_db(logger=logger, db_path=kwargs[f"{runner_name}.db"])

    match runner_name:
        case "init":
            runner = InitRunner(
                db=db,
                logger=logger,
                min_year=kwargs["init.min"],
                max_year=kwargs["init.max"],
            )
        case "search":
            runner = SearchRunner(
                db=db,
                logger=logger,
                megajournal_name=kwargs["search.journal"],
            )
        case "openalex":
            runner = OpenAlexRunner(
                db=db,
                logger=logger,
                email=kwargs["openalex.email"],
            )
        case "jats":
            runner = JATSRunner(
                db=db,
                logger=logger,
                plos_zip_fp=kwargs["jats.plos_zip"],
            )
        case "pandoc":
            runner = PandocRunner(
                db=db,
                logger=logger,
                pandoc_uri=kwargs["pandoc.uri"],
            )
        case "analyze":
            runner = AnalysisRunner(
                db=db,
                logger=logger,
                system_prompt_id=kwargs["analyze.system_prompt"],
                index=kwargs["analyze.index"],
                stride=kwargs["analyze.stride"],
                auth_key=kwargs["analyze.auth"],
                backend=kwargs["analyze.backend"],
                ollama_endpoint=kwargs["analyze.ollama"],
            )
        case _:
            return 1

    return runner.execute()
