from logging import Logger

from pandas import DataFrame

from aius.db import DB
from aius.prompts import *
from aius.runners.runner import Runner


class InitRunner(Runner):
    def __init__(
        self,
        logger: Logger,
        db: DB,
        min_year: int,
        max_year: int,
    ) -> None:
        self.logger: Logger = logger

        # Set constants
        self.db: DB = db
        self.min_year: int = min_year
        self.max_year: int = max_year
        self.logger.info(msg=f"Minimum year: {self.min_year}")
        self.logger.info(msg=f"Maximum year: {self.max_year}")

        # Natural science OpenAlex field constants
        self.ns_fields: list[tuple[str, int]] = [
            ("Agricultural and Biological Sciences", 11),
            ("Environmental Science", 23),
            ("Biochemistry, Genetics and Molecular Biology", 13),
            ("Immunology and Microbiology", 24),
            ("Neuroscience", 28),
            ("Earth and Planetary Sciences", 19),
            ("Physics and Astronomy", 31),
            ("Chemistry", 16),
        ]

        # Journal search keywords
        self.search_keywords: list[str] = [
            r'"Deep Learning"',
            r'"Deep Neural Network"',
            r'"Hugging Face"',
            r'"Model Checkpoint"',
            r'"Model Weights"',
            r'"Pre-Trained Model"',
        ]

        # LLM Prompts
        self.llm_prompts: list[COSTAR_SystemPrompt] = [
            USES_DL_PROMPT,
            USES_PTMS_PROMPT,
            IDENTIFY_PTMS_PROMPT,
            IDENTIFY_PTM_REUSE_PROMPT,
            IDENTIFY_PTM_USAGE_IN_SCIENTIFIC_PROCESS,
        ]

        # Create range of years
        self.year_range: range = range(self.min_year, self.max_year + 1)
        self.logger.info(msg=f"Years to store: {list(self.year_range)}")

    def _write_data_to_table(self, table: str, data: dict[str, list]) -> None:
        self.logger.info(msg=f"Writing data to the `{table}` table")
        self.logger.debug(msg=f"Data: {data}")
        DataFrame(data=data).to_sql(
            name=table,
            con=self.db.engine,
            if_exists="append",
            index=True,
            index_label="_id",
        )
        self.logger.info(msg=f"Wrote data to the `{table}` table")

    def execute(self) -> int:
        # Write LLM prompts
        self._write_data_to_table(
            table="_llm_prompts",
            data={
                "tag": [p.tag for p in self.llm_prompts],
                "prompt": [p.create_prompt() for p in self.llm_prompts],
                "json_string": [p.model_dump_json(indent=4) for p in self.llm_prompts],
            },
        )

        # Write OpenAlex natural science field filter
        self._write_data_to_table(
            table="_openalex_natural_science_fields",
            data={
                "field": [field[0] for field in self.ns_fields],
                "openalex_id": [field[1] for field in self.ns_fields],
            },
        )

        # Write search keywords
        self._write_data_to_table(
            table="_search_keywords",
            data={
                "keyword": self.search_keywords,
            },
        )

        # Write years
        self._write_data_to_table(
            table="_years",
            data={
                "year": list(self.year_range),
            },
        )

        return 0
