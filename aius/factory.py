"""
Entrypoint for runners.

Copyright 2025 (C) Nicholas M. Synovic

"""

from abc import ABC, abstractmethod
from logging import Logger

from aius.db import DB, connect_to_db
from aius.init import InitRunner
from aius.runners.analysis import AnalysisRunner
from aius.runners.jats import JATSRunner
from aius.runners.openalex import OpenAlexRunner
from aius.runners.pandoc import PandocRunner
from aius.runners.search import SearchRunner


class Runner(ABC):  # noqa: D101
    def __init__(self, name: str, db: DB, logger: Logger) -> None:  # noqa: D107
        self.logger: Logger = logger
        self.name: str = name
        self.db: DB = db

    @abstractmethod
    def execute(self) -> int: ...  # noqa: D102


# Factory method design pattern implementation
def runner_factory(  # noqa: D103
    logger: Logger,
    runner_name: str,
    **kwargs,  # noqa: ANN003
) -> Runner | int:
    logger.info("%s kwargs: %s", runner_name, kwargs)

    # Connect to the database
    db: DB = connect_to_db(logger=logger, db_path=kwargs[f"{runner_name}.db"])

    match runner_name:
        case "init":  # Step 0
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

    return runner
