from abc import ABC, abstractmethod
from logging import Logger


class Runner(ABC):
    @abstractmethod
    def execute(self) -> int: ...
