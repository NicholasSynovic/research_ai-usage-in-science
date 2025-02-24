from os.path import abspath
from pathlib import Path

import pandas
from pandas import DataFrame
from sqlalchemy import (
    Column,
    Engine,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
)

from src import JOURNALS, SEARCH_KEYWORDS, YEARS


class DB:
    def __init__(self, fp: Path) -> None:
        self.fp: Path = Path(abspath(path=fp))
        self.engine: Engine = create_engine(url=f"sqlite:///{self.fp}")
        self.metadata: MetaData = MetaData()

    def createTables(self) -> None:
        _: Table = Table(
            "years",
            self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("year", Integer, nullable=False),
        )

        _: Table = Table(
            "keywords",
            self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("keyword", String, nullable=False),
        )

        _: Table = Table(
            "journals",
            self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("journal", String, nullable=False),
        )

        _: Table = Table(
            "documents",
            self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("doi", String, nullable=False, unique=True),
        )

        _: Table = Table(
            "search_results",
            self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column(
                "document_id",
                Integer,
                ForeignKey("documents.id"),
                nullable=False,
            ),
            Column("response_id", Integer, nullable=False),
        )

        _: Table = Table(
            "search_responses",
            self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column(
                "year",
                Integer,
                ForeignKey("years.id"),
                nullable=False,
            ),
            Column(
                "keyword",
                Integer,
                ForeignKey("keywords.id"),
                nullable=False,
            ),
            Column(
                "journal",
                Integer,
                ForeignKey("journals.id"),
                nullable=False,
            ),
            Column("url", String, nullable=False),
            Column("page", Integer, nullable=False),
            Column("status_code", Integer, nullable=False),
            Column("html", String, nullable=False),
        )

        _: Table = Table(
            "openalex_responses",
            self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column(
                "document_id",
                Integer,
                ForeignKey("documents.id"),
                nullable=False,
            ),
            Column("url", String, nullable=False),
            Column("status_code", Integer, nullable=False),
            Column("html", String, nullable=False),
        )

        self.metadata.create_all(bind=self.engine, checkfirst=True)

    def writeConstants(self) -> None:
        YEARS.to_sql(
            name="years",
            con=self.engine,
            if_exists="append",
            index=True,
            index_label="id",
        )
        SEARCH_KEYWORDS.to_sql(
            name="keywords",
            con=self.engine,
            if_exists="append",
            index=True,
            index_label="id",
        )
        JOURNALS.to_sql(
            name="journals",
            con=self.engine,
            index=True,
            if_exists="append",
            index_label="id",
        )

    def readTableToDF(self, table: str) -> DataFrame:
        return pandas.read_sql_table(
            table_name=table,
            con=self.engine,
            index_col="id",
        )
