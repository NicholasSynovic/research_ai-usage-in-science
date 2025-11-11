from logging import Logger

from aius.runners.init import InitRunner


def init(logger: Logger, **kwargs) -> None:
    logger.debug(msg=f"init kwargs: {kwargs}")
    runner: InitRunner = InitRunner(
        db_path=kwargs["init.db"],
        min_year=kwargs["init.min"],
        max_year=kwargs["init.max"],
    )
    runner.execute(logger=logger)
