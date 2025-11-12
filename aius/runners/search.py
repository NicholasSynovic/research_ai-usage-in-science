from logging import Logger

from aius.db import DB
from aius.runners.runner import Runner
from aius.search.megajournal import MegaJournal
from aius.search.plos import PLOS


class SearchRunner(Runner):
    def __init__(self, logger: Logger, db: DB, journal: str) -> None:
        self.journal: MegaJournal | None
        match journal:
            case "plos":
                self.journal = PLOS(logger=logger, db=db)
            case _:
                self.journal = None

    def execute(self, logger: Logger) -> int:
        if self.journal is None:
            return 1

        [print(f) for f in self.journal.keyword_year_products]

        return 0
