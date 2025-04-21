from os.path import abspath
from pathlib import Path

import pandas
from pandas import DataFrame
from sqlalchemy import (
    JSON,
    Boolean,
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
            "search_results",
            self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column(
                "document_id",
                Integer,
                ForeignKey("documents.id"),
                nullable=False,
            ),
            Column(
                "response_id",
                Integer,
                ForeignKey("search_responses.id"),
                nullable=False,
            ),
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

        _: Table = Table(
            "document_filter",
            self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column(
                "document_id",
                Integer,
                ForeignKey("documents.id"),
                nullable=False,
            ),
            Column(
                "openalex_response_id",
                Integer,
                ForeignKey("openalex_responses.id"),
                nullable=False,
            ),
            Column("retracted", Boolean, nullable=False),
            Column("open_access", Boolean, nullable=False),
            Column("cited_by_count", Integer, nullable=False),
            Column("fields", String, nullable=False),
            Column("natural_science_fields", String, nullable=False),
            Column("is_natural_science", Boolean, nullable=False),
        )

        _: Table = Table(
            "author_agreement",
            self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column(
                "document_id",
                Integer,
                ForeignKey("documents.id"),
                nullable=False,
            ),
            Column("uses_dl", Boolean, nullable=False),
            Column("uses_ptms", Boolean, nullable=False),
            Column("ptm_reuse_pairings", JSON, nullable=False),
        )

        self.metadata.create_all(bind=self.engine, checkfirst=True)

    def writeConstants(self) -> None:
        YEARS.to_sql(
            name="years",
            con=self.engine,
            index=False,
            if_exists="append",
        )
        SEARCH_KEYWORDS.to_sql(
            name="keywords",
            con=self.engine,
            index=False,
            if_exists="append",
        )
        JOURNALS.to_sql(
            name="journals",
            con=self.engine,
            index=False,
            if_exists="append",
        )

    def readTableToDF(self, table: str) -> DataFrame:
        return pandas.read_sql_table(
            table_name=table,
            con=self.engine,
            index_col="id",
        )

    def getPLOSPapersPerKeyword(self) -> DataFrame:
        sqlQuery: str = """
SELECT search_results.*, keywords.keyword FROM search_results
INNER JOIN search_responses ON search_results.response_id = search_responses.id
INNER JOIN keywords ON search_responses.keyword = keywords.id
WHERE search_responses.journal = 2;
"""
        return pandas.read_sql_query(
            sql=sqlQuery,
            con=self.engine,
            index_col="id",
        )

    def getPLOSPapersPerYear(self) -> DataFrame:
        sqlQuery: str = """
SELECT search_results.*, years.year FROM search_results
INNER JOIN search_responses ON search_results.response_id = search_responses.id
INNER JOIN years ON search_responses.year = years.id
WHERE search_responses.journal = 2;
"""
        return pandas.read_sql_query(
            sql=sqlQuery,
            con=self.engine,
            index_col="id",
        )

    def get_PLOS_OA_PapersPerYear(self) -> DataFrame:
        sqlQuery: str = """
SELECT search_results.*, years.year, openalex_responses.id AS oaID FROM search_results
INNER JOIN search_responses ON search_results.response_id = search_responses.id
INNER JOIN years ON search_responses.year = years.id
INNER JOIN openalex_responses ON search_results.document_id = openalex_responses.document_id
WHERE search_responses.journal = 2;
"""  # noqa: E501
        return pandas.read_sql_query(
            sql=sqlQuery,
            con=self.engine,
            index_col="id",
        )

    def get_PLOS_OA_NS_PapersPerYear(self) -> DataFrame:
        sqlQuery: str = """
SELECT search_results.*, years.year, openalex_responses.id as oaID, document_filter.cited_by_count FROM search_results
INNER JOIN search_responses ON search_results.response_id = search_responses.id
INNER JOIN years ON search_responses.year = years.id
INNER JOIN openalex_responses ON search_results.document_id = openalex_responses.document_id
INNER JOIN document_filter ON oaID = document_filter.openalex_response_id
WHERE
    document_filter.cited_by_count >= 1 AND
    document_filter.is_natural_science = 1 AND
    search_responses.journal = 2;
"""  # noqa: E501
        return pandas.read_sql_query(
            sql=sqlQuery,
            con=self.engine,
            index_col="id",
        )

    def getAuthorAgreementDOIs(self) -> DataFrame:
        sqlQuery: str = """
SELECT documents.doi FROM author_agreement
INNER JOIN documents ON author_agreement.document_id = documents.id;
"""
        return pandas.read_sql_query(sql=sqlQuery, con=self.engine)
