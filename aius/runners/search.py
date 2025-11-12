from logging import Logger

from aius.db import DB
from aius.runners.runner import Runner
from aius.search.megajournal import MegaJournal
from aius.search.plos import PLOS


class SearchRunner(Runner):
    def __init__(self, logger: Logger, db: DB, journal: str) -> None:
        self.logger: Logger = logger

        self.journal: MegaJournal | None
        match journal:
            case "plos":
                self.journal = PLOS(logger=self.logger, db=db)
            case _:
                self.journal = None

        if self.journal is None:
            self.logger.error(msg=f"Journal is set to None (journal={journal})")
        else:
            self.logger.info(msg=f"Identified journal as {self.journal.megajournal}")

    def execute(self) -> int:
        if self.journal is None:
            self.logger.info(msg="Journal is None. Returning 1")
            return 1

        self.logger.info(msg=f"Executing {self.journal.megajournal} search")
        self.journal.search()

        return 0
