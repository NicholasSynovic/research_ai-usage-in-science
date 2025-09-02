from pathlib import Path

from sqlalchemy import (
    Column,
    Engine,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
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
            "search",
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
        self.metadata.create_all(bind=self.engine, checkfirst=True)

    def _write_constants(self) -> None:
        pass
