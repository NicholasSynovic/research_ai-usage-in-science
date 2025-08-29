from pathlib import Path

from sqlalchemy import (
    Engine,
    MetaData,
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
        self.metadata.create_all(bind=self.engine, checkfirst=True)

    def _write_constants(self) -> None:
        pass
