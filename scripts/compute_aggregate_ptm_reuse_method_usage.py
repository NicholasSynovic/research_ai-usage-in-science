import json
from pathlib import Path

import click
import pandas
from pandas import DataFrame

from aius.db import DB


def get_aa_data(db: DB) -> DataFrame:
    sql_query: str = """
    SELECT
        plos_author_agreement_papers.*
    FROM
        plos_author_agreement_papers;
    """

    return pandas.read_sql_query(
        sql=sql_query,
        con=db.engine,
        index_col="_id",
    )


def read_json(fp: Path, aa_df: DataFrame) -> DataFrame:
    df_data: dict[str, list[int | list]] = {
        "_id": [],
        "reuse": [],
    }

    data: dict
    with open(file=fp, mode="r") as jfp:
        data = json.load(fp=jfp)
        jfp.close()

    key: int
    for key in data.keys():
        if data[key] == []:
            continue

        if data[key][0]["model"] == "None":
            continue

        if data[key][0]["model"] == "":
            continue

        datum: list[str] = []
        for reuse_dict in data[key]:
            datum.append(reuse_dict["classification"])

        df_data["_id"].append(key)
        df_data["reuse"].append(datum)

    return DataFrame(data=df_data)


def compute_gpt(gpt_df: DataFrame) -> None:
    gpt_df = gpt_df.explode(column="reuse")
    print(gpt_df["reuse"].value_counts())


def compute_aa(aa_df: DataFrame) -> None:
    aa_df["reuse"] = aa_df["ptm_name_reuse_type"].apply(
        lambda x: json.loads(s=x)["reuse"]
    )
    aa_df = aa_df[aa_df["reuse"].str.len() != 0]
    aa_df = aa_df.explode(column="reuse")
    print(aa_df["reuse"].value_counts())


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

    # compute_gpt(gpt_df)
    compute_aa(aa_df=aa_df)

    pass


if __name__ == "__main__":
    main()
