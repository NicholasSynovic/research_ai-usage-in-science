from logging import Logger
from os import listdir
from pathlib import Path

import click
import pandas as pd
from pandas import DataFrame

from aius.db import DB


def get_parquet_files(parquet_dir: Path) -> list[Path]:
    files: list[str] = listdir(path=parquet_dir)
    return [Path(parquet_dir, file).resolve() for file in files]


def get_dataframes(parquet_files: list[Path]) -> list[DataFrame]:
    return [pd.read_parquet(path=file) for file in parquet_files]


@click.command()
@click.option(
    "--parquet-dir",
    type=Path,
    required=True,
)
@click.option(
    "--db-path",
    type=Path,
    required=True,
)
@click.option(
    "--db-table",
    type=str,
    required=True,
)
def main(parquet_dir: Path, db_path: Path, db_table: str) -> None:
    logger: Logger = Logger(name="parquet2db")

    abs_parquet_dir: Path = parquet_dir.resolve()
    parquet_files: list[Path] = get_parquet_files(parquet_dir=abs_parquet_dir)

    db: DB = DB(logger=logger, db_path=db_path.resolve())

    dfs: list[DataFrame] = get_dataframes(parquet_files=parquet_files)
    df: DataFrame = pd.concat(objs=dfs, ignore_index=True)

    print(df)


if __name__ == "__main__":
    main()
