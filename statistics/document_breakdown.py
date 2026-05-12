from json import loads
from logging import Logger
from pathlib import Path

import pandas as pd
from pandas import DataFrame

from aius.db import DB

TABLE: str = "uses_ptms_analysis"


def set_dataframe_formatting(df: DataFrame) -> DataFrame:
    df["model_response"] = df["model_response"].replace(
        to_replace="",
        value=float("NaN"),
        inplace=False,
    )
    df = df.dropna(inplace=False, ignore_index=True)
    df["model_response"] = df["model_response"].apply(loads)
    df = df[df["model_response"].apply(lambda d: d.get("result") is True)]
    df.reset_index(drop=True, inplace=True)
    df.rename(columns={"user_prompt": "markdown"}, inplace=True)
    return df


def main() -> None:
    logger: Logger = Logger(name="")
    db_path: Path = Path("../data/aius_12-15-2025_1.db").resolve()
    db: DB = DB(logger=logger, db_path=db_path)

    sql: str = f"""
SELECT {TABLE}.*, articles.megajournal FROM {TABLE}
JOIN articles ON articles.doi = {TABLE}.doi;
"""

    df: DataFrame = pd.read_sql(sql=sql, con=db.engine, index_col="_id")
    df = set_dataframe_formatting(df=df)

    print(df["megajournal"].value_counts())


main()
