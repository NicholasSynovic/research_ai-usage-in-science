from pathlib import Path

from sqlalchemy import (
    Column,
    Engine,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    text,
)


class DB:
    def __init__(self, db_path: Path) -> None:
        # Establish class variables
        self.db_path = db_path
        self.metadata: MetaData = MetaData()

        # Connect to the database
        self.engine: Engine = create_engine(url=f"sqlite:///{self.db_path}")

        # Create tables and write constants if they do not exists
        self._create_tables()
        self._write_constants()

    def _create_tables(self) -> None:
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
        )

        # Papers table
        _: Table = Table(
            "papers",
            self.metadata,
            Column("_id", Integer, primary_key=True),
            Column("doi", String),
        )

        # Searches to Papers table
        _: Table = Table(
            "searches_to_papers",
            self.metadata,
            Column("_id", Integer, primary_key=True),
            Column("search_id", Integer, ForeignKey("searches._id")),
            Column("paper_id", Integer, ForeignKey("papers._id")),
        )

        _: Table = Table(
            "openalex",
            self.metadata,
            Column("_id", Integer, primary_key=True),
            Column("cited_by_count", Integer),
            Column("json", String),
            Column("paper_id", Integer, ForeignKey("papers._id")),
            Column("status_code", Integer),
            Column("topic_0", String),
            Column("topic_1", String),
            Column("topic_2", String),
            Column("url", String),
        )

        self.metadata.create_all(bind=self.engine, checkfirst=True)

    def _write_constants(self) -> None:
        pass

    def get_last_row_id(self, table_name: str) -> int:
        sql = text(f"SELECT _id FROM {table_name} ORDER BY _id DESC;")
        try:
            return self.engine.connect().execute(statement=sql).first()[0]
        except TypeError:
            return 0
