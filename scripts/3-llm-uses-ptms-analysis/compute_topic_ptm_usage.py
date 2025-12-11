from collections import defaultdict
from pathlib import Path
from pprint import pprint as print

import click
import pandas
from pandas import DataFrame, Series

from aius.db import DB


def get_aa(db: DB) -> DataFrame:
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

    return pandas.read_sql_query(sql=sql_query, con=db.engine, index_col="_id")


def compute(df: DataFrame) -> None:
    data: dict[str, int] = defaultdict(int)

    row: Series
    for _, row in df.iterrows():
        unique_topics: set[str] = {row["topic_0"], row["topic_1"], row["topic_2"]}

        for topic in unique_topics:
            data[topic] += 1

    print(data)


@click.command()
@click.option(
    "-i",
    required=True,
    type=lambda x: Path(x).resolve(),
)
@click.option(
    "-d",
    required=True,
    type=lambda x: Path(x).resolve(),
)
def main(i: Path, d: Path) -> None:
    db: DB = DB(db_path=d)
    aa_df: DataFrame = get_aa(db=db)

    df: DataFrame = pandas.read_json(path_or_buf=i).T
    df["result"] = df["result"].astype(dtype=bool)

    df = df[df["result"] == True]
    df = df.join(other=aa_df)

    compute(df=df)


if __name__ == "__main__":
    main()
