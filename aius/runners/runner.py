"""
Runner interface.

Copyright (C) 2025 Nicholas M. Synovic
"""

from abc import ABC, abstractmethod
from logging import Logger

from aius.db import DB


class Runner(ABC):  # noqa: D101
    def __init__(self, name: str, db: DB, logger: Logger) -> None:  # noqa: D107
        self.logger: Logger = logger
        self.name: str = name
        self.db: DB = db

    @abstractmethod
    def execute(self) -> int: ...  # noqa: D102
