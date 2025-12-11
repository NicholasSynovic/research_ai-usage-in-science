import json
from collections import defaultdict
from pathlib import Path
from pprint import pprint as print

import click
import pandas
from pandas import DataFrame, Series
from pandas.core.groupby import DataFrameGroupBy

from aius.db.db import DB


def get_db_df(db: DB) -> DataFrame:
    sql_query: str = """
    SELECT
        plos_natural_science_papers.*,
        plos_paper_openalex_metadata.topic_0,
        plos_paper_openalex_metadata.topic_1,
        plos_paper_openalex_metadata.topic_2
    FROM
        plos_natural_science_papers
    JOIN
        plos_paper_openalex_metadata
    ON
        plos_natural_science_papers.plos_paper_id = plos_paper_openalex_metadata.plos_paper_id;
    """

    return pandas.read_sql_query(
        sql=sql_query,
        con=db.engine,
        index_col="_id",
    )


def compute_proportion_per_topic(df: DataFrame) -> None:
    data: dict[str, int] = defaultdict(int)

    row: Series
    for _, row in df.iterrows():
        data[row["topic_0"]] += 1
        data[row["topic_1"]] += 1
        data[row["topic_2"]] += 1

    print(data)
    print(sum(data.values()) - 32)


@click.command()
@click.option(
    "-d",
    required=True,
    type=lambda x: Path(x).resolve(),
)
@click.option(
    "-j",
    required=True,
    type=lambda x: Path(x).resolve(),
)
def main(d: Path, j: Path) -> None:
    db: DB = DB(db_path=d)

    df: DataFrame = pandas.read_json(path_or_buf=j).T
    df["result"] = df["result"].astype(dtype=bool)

    db_df: DataFrame = get_db_df(db=db)

    df = df.join(other=db_df)

    compute_proportion_per_topic(df=df)


if __name__ == "__main__":
    main()
