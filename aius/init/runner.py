"""
Initialize application runner.

Copyright 2025 (C) Nicholas M. Synovic

"""

from logging import Logger

from aius.analyze import SYSTEM_PROMPT_TAG_MAPPING_DF
from aius.db import DB
from aius.init import (
    JOURNAL_SEARCH_KEYWORDS,
    NATURAL_SCIENCE_OA_FIELDS,
    compute_journal_search_years,
)
from aius.runner import Runner


class InitRunner(Runner):  # noqa: D101
    def __init__(  # noqa: D107
        self,
        db: DB,
        logger: Logger,
        min_year: int,
        max_year: int,
    ) -> None:
        # Set constants
        super().__init__(name="init", db=db, logger=logger)
        self.min_year: int = min_year
        self.max_year: int = max_year
        self.logger.info("Minimum year: %s", self.min_year)
        self.logger.info("Maximum year: %s", self.max_year)

    def execute(self) -> int:  # noqa: D102
        # Write LLM prompts
        self.db.write_dataframe_to_table(
            df=SYSTEM_PROMPT_TAG_MAPPING_DF,
            table_name="_llm_prompts",
        )

        # Write OpenAlex natural science field filter
        self.db.write_dataframe_to_table(
            df=NATURAL_SCIENCE_OA_FIELDS,
            table_name="_openalex_natural_science_fields",
        )

        # Write search keywords
        self.db.write_dataframe_to_table(
            table_name="_search_keywords", df=JOURNAL_SEARCH_KEYWORDS
        )

        # Write years
        self.db.write_dataframe_to_table(
            df=compute_journal_search_years(
                min_year=self.min_year,
                max_year=self.max_year,
            ),
            table_name="_years",
        )

        return 0
