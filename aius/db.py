"""
SQLite3 Database class implementation.

Copyright (C) 2025 Nicholas M. Synovic
"""

import contextlib
from pathlib import Path
from string import Template

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Engine,
    ForeignKey,
    Integer,
    MetaData,
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

    def __init__(self, db_path: Path) -> None:
        """
        Initialize a DB object.

        Args:
          db_path: The path to the SQLite database file.  This file will be
            created if it doesn't exist.

        """
        # Establish class variables
        self.db_path = db_path
        self.metadata: MetaData = MetaData()

        # Connect to the database
        self.engine: Engine = create_engine(url=f"sqlite:///{self.db_path}")

        # Create tables and write constants if they do not exists
        self._create_tables()

    def _create_tables(self) -> None:
        """Create tables in the database if they do not already exist."""
        # Search table
        _: Table = Table(
            "searches",
            self.metadata,
            Column("_id", Integer, primary_key=True),
            Column("html", String),
            Column("journal", String),
            Column("keyword", String),
            Column("page", Integer),
            Column("status_code", Integer),
            Column("url", String),
            Column("year", Integer),
            Column("timestamp", DateTime),
        )

        # Papers table
        _: Table = Table(
            "papers",
            self.metadata,
            Column("_id", Integer, primary_key=True),
            Column("doi", String),
            Column("html", String),
            Column("md", String),
        )

        # Searches to Papers table
        _: Table = Table(
            "searches_to_papers",
            self.metadata,
            Column("_id", Integer, primary_key=True),
            Column("search_id", Integer, ForeignKey("searches._id")),
            Column("paper_id", Integer, ForeignKey("papers._id")),
        )

        # OpenAlex table
        _: Table = Table(
            "openalex",
            self.metadata,
            Column("_id", Integer, primary_key=True),
            Column("cited_by_count", Integer),
            Column("json", String),
            Column("open_access", Boolean),
            Column("paper_id", Integer, ForeignKey("papers._id")),
            Column("status_code", Integer),
            Column("topic_0", String),
            Column("topic_1", String),
            Column("topic_2", String),
            Column("url", String),
        )

        # Natural Science Papers
        _: Table = Table(
            "ns_papers",
            self.metadata,
            Column("_id", Integer, primary_key=True),
            Column("paper_id", Integer, ForeignKey("papers._id")),
        )

        self.metadata.create_all(bind=self.engine, checkfirst=True)

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
            last_row_id = int(self.engine.connect().execute(statement=sql).first()[0])

        return last_row_id
