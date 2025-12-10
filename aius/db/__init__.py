"""
SQLite3 Database class implementation.

Copyright (C) 2025 Nicholas M. Synovic
"""

import contextlib
import warnings
from logging import Logger
from pathlib import Path
from string import Template

import pandas as pd
from pandas import DataFrame
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Engine,
    Integer,
    MetaData,
    Row,
    String,
    Table,
    TextClause,
    create_engine,
    text,
)

DEFAULT_DATABASE_PATH: Path = Path("aius.sqlite3").resolve()


class DB:  # noqa: D101
    def __init__(self, logger: Logger, db_path: Path) -> None:  # noqa: D107
        # Supress warnings
        warnings.filterwarnings(action="ignore")

        # Establish class variables
        self.metadata: MetaData = MetaData()

        # Connect to the database
        uri: str = f"sqlite:///{db_path}"
        self.engine: Engine = create_engine(url=uri)
        self.logger: Logger = logger

        self.logger.info("Connected to SQLite3 database: %s", uri)

        # Create tables if they do not exists
        self._create_tables()

        self.logger.info("Created tables if they did not already exist")

    def _create_tables(self) -> None:
        # CO-STAR LLM prompts
        _: Table = Table(
            "_llm_prompts",
            self.metadata,
            Column("_id", Integer, primary_key=True),
            Column("tag", String),
            Column("prompt", String),
            Column("json_string", String),
        )

        # OpenAlex natural science field filter
        _: Table = Table(
            "_openalex_natural_science_fields",
            self.metadata,
            Column("_id", Integer, primary_key=True),
            Column("openalex_id", Integer),
            Column("field", String),
        )

        # Keywords to search journals with
        _: Table = Table(
            "_search_keywords",
            self.metadata,
            Column("_id", Integer, primary_key=True),
            Column("keyword", String),
        )

        # Years we are searching documents for
        _: Table = Table(
            "_years",
            self.metadata,
            Column("_id", Integer, primary_key=True),
            Column("year", Integer),
        )

        # Search table
        _: Table = Table(
            "searches",
            self.metadata,
            Column("_id", Integer, primary_key=True),
            Column("timestamp", DateTime),
            Column("megajournal", String),
            Column("search_keyword", String),
            Column("year", Integer),
            Column("url", String),
            Column("page", Integer),
            Column("status_code", String),
            Column("json_data", String),
        )

        # Articles table
        _: Table = Table(
            "articles",
            self.metadata,
            Column("_id", Integer, primary_key=True),
            Column("doi", String),
            Column("title", String),
            Column("megajournal", String),
            Column("journal", String),
        )

        # OpenAlex table
        _: Table = Table(
            "openalex",
            self.metadata,
            Column("_id", Integer, primary_key=True),
            Column("timestamp", DateTime),
            Column("doi", String),
            Column("cited_by_count", Integer),
            Column("open_access", Boolean),
            Column("topic_0", String),
            Column("topic_1", String),
            Column("topic_2", String),
            Column("json_data", String),
        )

        # JATS table
        _: Table = Table(
            "jats",
            self.metadata,
            Column("_id", Integer, primary_key=True),
            Column("doi", String),
            Column("jats_xml", String),
        )

        # Markdown table
        _: Table = Table(
            "markdown",
            self.metadata,
            Column("_id", Integer, primary_key=True),
            Column("doi", String),
            Column("markdown", String),
        )

        # uses_dl analyis table
        _: Table = Table(
            "uses_dl_analysis",
            self.metadata,
            Column("_id", Integer, primary_key=True),
            Column("doi", String),
            Column("response", String),
            Column("reasoning", String),
        )

        self.metadata.create_all(bind=self.engine, checkfirst=True)

        view_sql = """
CREATE VIEW IF NOT EXISTS natural_science_article_dois AS
WITH field_values AS (
    SELECT
        field
    FROM
        _openalex_natural_science_fields
)
SELECT
    DISTINCT oa.doi
FROM
    openalex oa
WHERE
    oa.cited_by_count > 0
    AND (
        (
            oa.topic_0 IN field_values
            AND oa.topic_1 IN field_values
        )
        OR (
            oa.topic_0 IN field_values
            AND oa.topic_2 IN field_values
        )
        OR (
            oa.topic_1 IN field_values
            AND oa.topic_2 IN field_values
        )
    )
;
"""

        # Execute the SQL to create the view
        with self.engine.connect() as conn:
            conn.execute(text("DROP VIEW IF EXISTS natural_science_article_dois;"))
            conn.execute(text(view_sql))
            conn.commit()

        self.logger.info("Created `natural_science_article_dois` view")

    def get_search_keywords(self) -> list[str]:  # noqa: D102
        df: DataFrame = pd.read_sql_table(
            table_name="_search_keywords",
            con=self.engine,
            index_col="_id",
        )

        self.logger.info("Retrieved search keywords: %s", df)

        return df["keyword"].tolist()

    def get_years(self) -> list[int]:  # noqa: D102
        df: DataFrame = pd.read_sql_table(
            table_name="_years",
            con=self.engine,
            index_col="_id",
        )

        self.logger.info("Retrieved years: %s", df)

        return df["year"].tolist()

    def get_llm_prompt(self, llm_prompt_id: str) -> str:
        df: DataFrame = pd.read_sql_table(
            table_name="_llm_prompts",
            con=self.engine,
            index_col="_id",
        )

        return df[df["tag"] == llm_prompt_id]["prompt"].to_list()[0]

    def get_last_row_id(self, table_name: str) -> int:  # noqa: D102
        last_row_id: int = -1

        sql_template = Template(template="SELECT _id FROM ${tn} ORDER BY _id DESC;")
        sql: TextClause = text(sql_template.substitute(tn=table_name))

        self.logger.debug("Created SQL query: %s", sql)

        with contextlib.suppress(TypeError):
            # Removes try - except in code; pretty neat!
            last_row: Row | None = self.engine.connect().execute(statement=sql).first()

            if last_row is not None:
                last_row_id = int(last_row[0])
            else:
                self.logger.debug("Last row returned `None`")

        return last_row_id

    def write_dataframe_to_table(self, table_name: str, df: DataFrame) -> None:
        self.logger.info("Writing data to the `%s` table", table_name)
        self.logger.debug("Data: %s", table_name)
        df.to_sql(
            name=table_name,
            con=self.engine,
            if_exists="append",
            index=True,
            index_label="_id",
        )
        self.logger.info("Wrote data to the `%s` table", table_name)

    def read_table_to_dataframe(self, table_name: str) -> DataFrame:
        self.logger.info("Reading data to the `%s` table", table_name)
        self.logger.debug("Data: %s", table_name)
        return pd.read_sql_table(
            table_name=table_name,
            con=self.engine,
            index_col="_id",
        )
