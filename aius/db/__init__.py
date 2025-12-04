"""
SQLite3 Database class implementation.

Copyright (C) 2025 Nicholas M. Synovic
"""

import contextlib
import warnings
from logging import Logger
from pathlib import Path
from string import Template

import pandas
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


class DB:
    """
    Represents a database instance for managing scientific paper data.

    Provides methods for creating tables, managing data, and retrieving
    information.
    """

    def __init__(self, logger: Logger, db_path: Path) -> None:
        """
        Initialize a DB object.

        Args:
          db_path: The path to the SQLite database file.  This file will be
            created if it doesn't exist.

        """
        # Supress warnings
        warnings.filterwarnings(action="ignore")

        # Establish class variables
        self.metadata: MetaData = MetaData()

        # Connect to the database
        uri: str = f"sqlite:///{db_path}"
        self.engine: Engine = create_engine(url=uri)
        logger.info(msg=f"Connected to SQLite3 database: {uri}")

        # Create tables if they do not exists
        self._create_tables()

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

        # # PLOS Natural Science Paper Content
        # _: Table = Table(
        #     "plos_natural_science_paper_content",
        #     self.metadata,
        #     Column("_id", Integer, primary_key=True),
        #     Column("plos_paper_id", Integer, ForeignKey("plos_paper_dois._id")),
        #     Column("raw_jats_xml", String),
        #     Column("formatted_jats_xml", String),
        #     Column("raw_md", String),
        #     Column("formatted_md", String),
        #     Column("raw_jats_xml_token_count", Integer),
        #     Column("formatted_jats_xml_token_count", Integer),
        #     Column("raw_md_token_count", Integer),
        #     Column("formatted_md_token_count", Integer),
        # )

        # # Pilot Study PLOS Paper
        # _: Table = Table(
        #     "plos_pilot_study_papers",
        #     self.metadata,
        #     Column("_id", Integer, primary_key=True),
        #     Column("plos_paper_id", Integer, ForeignKey("plos_paper_dois._id")),
        #     Column("url", String),
        #     Column("json", String),
        #     Column("timestamp", DateTime),
        # )

        # # Author Agreement PLOS Papers
        # _: Table = Table(
        #     "plos_author_agreement_papers",
        #     self.metadata,
        #     Column("_id", Integer, primary_key=True),
        #     Column("plos_paper_id", Integer, ForeignKey("plos_paper_dois._id")),
        #     Column("uses_dl", Boolean),
        #     Column("uses_ptms", Boolean),
        #     Column("ptm_name_reuse_type", String),
        # )

        # # PLOS LLM Prompt Engineering papers
        # _: Table = Table(
        #     "plos_llm_prompt_engineering_papers",
        #     self.metadata,
        #     Column("_id", Integer, primary_key=True),
        #     Column("plos_paper_id", Integer, ForeignKey("plos_paper_dois._id")),
        # )

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
            conn.execute(text("DROP VIEW IF EXISTS topic_field_matches;"))
            conn.execute(text(view_sql))
            conn.commit()

    def get_search_keywords(self) -> list[str]:
        df: DataFrame = pandas.read_sql_table(
            table_name="_search_keywords",
            con=self.engine,
            index_col="_id",
        )

        return df["keyword"].tolist()

    def get_years(self) -> list[int]:
        df: DataFrame = pandas.read_sql_table(
            table_name="_years",
            con=self.engine,
            index_col="_id",
        )

        return df["year"].tolist()

    def get_last_row_id(self, table_name: str) -> int:
        """
        Retrieve the ID of the last row in a specified table.

        Args:
          table_name: The name of the table to query.

        Returns:
          The ID of the last row in the table, or 0 if the table is empty.
          Returns -1 if a `TypeError` is raised during the database operation,
          indicating a potential problem with the database connection or query.

        """
        last_row_id: int = -1

        sql_template = Template(template="SELECT _id FROM ${tn} ORDER BY _id DESC;")
        sql: TextClause = text(sql_template.substitute(tn=table_name))

        with contextlib.suppress(TypeError):
            # Removes try - except in code; pretty neat!
            last_row: Row | None = self.engine.connect().execute(statement=sql).first()

            if last_row is not None:
                last_row_id = int(last_row[0])

        return last_row_id
