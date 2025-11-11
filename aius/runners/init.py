from logging import Logger
from pathlib import Path

from pandas import DataFrame

from aius.db import DB
from aius.prompts import *
from aius.runners.runner import Runner


class InitRunner(Runner):
    def __init__(self, db_path: Path, min_year: int, max_year: int) -> None:
        # Set constants
        self.db_path: Path = db_path
        self.min_year: int = min_year
        self.max_year: int = max_year

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
            IDENTIFY_PTMS_PROMPT,
            IDENTIFY_PTM_USAGE_IN_SCIENTIFIC_PROCESS,
        ]

        # Create range of years
        self.year_range: range = range(self.min_year, self.max_year + 1)

    def execute(self, logger: Logger) -> int:
        # Lambda function to simplify writing to the database
        write_data = lambda table, data: DataFrame(data=data).to_sql(
            name=table,
            con=db.engine,
            if_exists="append",
            index=True,
            index_label="_id",
        )

        # Connect to the database
        logger.info(msg=f"Connected to SQLite3 database: {self.db_path}")
        db: DB = DB(logger=logger, db_path=self.db_path)

        # Write LLM prompts
        table: str = "_llm_prompts"
        logger.info(msg=f"Writing LLM prompts to the `{table}` table")
        write_data(
            table=table,
            data={
                "tag": [p.tag for p in self.llm_prompts],
                "prompt": [p.create_prompt() for p in self.llm_prompts],
                "json_string": [p.model_dump_json(indent=4) for p in self.llm_prompts],
            },
        )
        logger.info(msg=f"Wrote LLM prompt to the `{table}` table")

        # Write OpenAlex natural science field filter
        table = "_openalex_natural_science_fields"
        logger.info(
            msg=f"Writing OpenAlex natural science fields to the `{table}` table"
        )
        write_data(
            table=table,
            data={
                "field": [field[0] for field in self.ns_fields],
                "openalex_id": [field[1] for field in self.ns_fields],
            },
        )
        logger.info(msg=f"Wrote OpenAlex natural science fields to the `{table}` table")

        # Write search keywords
        table = "_search_keywords"
        logger.info(msg=f"Writing search keywords to the `{table}` table")
        write_data(
            table=table,
            data={
                "keyword": self.search_keywords,
            },
        )
        logger.info(msg=f"Wrote search keywords to the `{table}` table")

        # Write years
        table = "_years"
        logger.info(msg=f"Writing years to the `{table}` table")
        write_data(
            table=table,
            data={
                "year": list(self.year_range),
            },
        )
        logger.info(msg=f"Wrote years to the `{table}` table")

        return 0
