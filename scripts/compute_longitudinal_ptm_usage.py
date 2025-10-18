import json
from pathlib import Path

import click
import pandas
from pandas import DataFrame, Series
from pandas.core.groupby import DataFrameGroupBy

from aius.db import DB


def get_oa_data(db: DB) -> DataFrame:
    sql_query: str = """
    SELECT plos_paper_openalex_metadata.* FROM plos_paper_openalex_metadata;
    """

    return pandas.read_sql_query(
        sql=sql_query,
        con=db.engine,
        index_col="_id",
    )


def get_aa_data(db: DB) -> DataFrame:
    sql_query: str = """
    SELECT
        plos_author_agreement_papers.*, plos_paper_openalex_metadata.json
    FROM
        plos_author_agreement_papers
    JOIN
        plos_paper_openalex_metadata
    ON
        plos_author_agreement_papers.plos_paper_id = plos_paper_openalex_metadata.plos_paper_id;
    """

    df: DataFrame = pandas.read_sql_query(
        sql=sql_query,
        con=db.engine,
        index_col="_id",
    )

    df["json"] = df["json"].apply(json.loads)
    df["year"] = df["json"].apply(lambda x: x["publication_year"])

    return df[["uses_ptms", "plos_paper_id", "year"]]


def read_json(fp: Path, aa_df: DataFrame) -> DataFrame:
    aa_copy_df: DataFrame = aa_df.copy()

    df: DataFrame = pandas.read_json(path_or_buf=fp).T

    df = df.join(other=aa_copy_df)

    df = df[["result", "plos_paper_id", "year"]]
    return df.rename(columns={"result": "uses_ptms"})


def compute(gpt_df: DataFrame) -> DataFrame:
    data: dict[str, list] = {
        "year": [],
        "count": [],
    }

    dfgb: DataFrameGroupBy = gpt_df.groupby(by="year")
    _df: DataFrame
    idx: int
    for idx, _df in dfgb:
        data["year"].append(idx)
        data["count"].append(_df.shape[0])

    return DataFrame(data=data)


@click.command()
@click.option(
    "--db-path",
    required=True,
    help="Path to database",
    type=lambda x: Path(x).resolve(),
)
@click.option(
    "--gpt-path",
    required=True,
    help="Path to gpt JSON",
    type=lambda x: Path(x).resolve(),
)
def main(db_path: Path, gpt_path: Path) -> None:
    db: DB = DB(db_path=db_path)

    aa_df: DataFrame = get_aa_data(db=db)
    gpt_df: DataFrame = read_json(fp=gpt_path, aa_df=aa_df)

    print(compute(gpt_df=gpt_df[gpt_df["uses_ptms"] == True]))
    print(compute(gpt_df=aa_df[aa_df["uses_ptms"] == True]))


if __name__ == "__main__":
    main()
