from logging import Logger


def init(logger: Logger, **kwargs) -> None:
    logger.debug(msg=f"kwargs: {kwargs}")
