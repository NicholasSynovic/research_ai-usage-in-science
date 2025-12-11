import json
from collections import defaultdict
from pathlib import Path

import click
import pandas
from pandas import DataFrame, Series
from pandas.core.groupby import DataFrameGroupBy

from aius.db.db import DB


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
        plos_author_agreement_papers.*, plos_paper_openalex_metadata.topic_0, plos_paper_openalex_metadata.topic_1, plos_paper_openalex_metadata.topic_2
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

    return df[
        [
            "uses_ptms",
            "plos_paper_id",
            "topic_0",
            "topic_1",
            "topic_2",
            "ptm_name_reuse_type",
        ]
    ]


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

        df_data["_id"].append(int(key))
        df_data["reuse"].append(datum)

    df: DataFrame = DataFrame(data=df_data).set_index(keys="_id")
    aa_copy_df: DataFrame = aa_df.copy()

    df = df.join(other=aa_copy_df)

    return df[["reuse", "uses_ptms", "topic_0", "topic_1", "topic_2"]]

    # df = df[["result", "plos_paper_id", "topic_0", "topic_1", "topic_2"]]
    # return df.rename(columns={"result": "uses_dl"})


def compute(gpt_df: DataFrame) -> DataFrame:
    data: dict[str, dict[str, int]] = {
        "a": defaultdict(int),
        "c": defaultdict(int),
        "d": defaultdict(int),
    }

    gpt_df = gpt_df.explode(column="reuse")

    for _, row in gpt_df.iterrows():
        if row["reuse"] == "adaptation_reuse":
            data["a"][row["topic_0"]] += 1
            data["a"][row["topic_1"]] += 1
            data["a"][row["topic_2"]] += 1

        if row["reuse"] == "conceptual_reuse":
            data["c"][row["topic_0"]] += 1
            data["c"][row["topic_1"]] += 1
            data["c"][row["topic_2"]] += 1

        if row["reuse"] == "deployment_reuse":
            data["d"][row["topic_0"]] += 1
            data["d"][row["topic_1"]] += 1
            data["d"][row["topic_2"]] += 1

    print(data)


def compute_aa(aa_df: DataFrame) -> DataFrame:
    aa_df = aa_df.copy()
    aa_df = aa_df[aa_df["uses_ptms"] == True]
    aa_df["reuse"] = aa_df["ptm_name_reuse_type"].apply(
        lambda x: json.loads(x)["reuse"]
    )

    aa_df = aa_df.explode(column="reuse")
    print(aa_df)

    data: dict[str, dict[str, int]] = {
        "a": defaultdict(int),
        "c": defaultdict(int),
        "d": defaultdict(int),
    }

    for _, row in aa_df.iterrows():
        if row["reuse"] == "adaptation":
            data["a"][row["topic_0"]] += 1
            data["a"][row["topic_1"]] += 1
            data["a"][row["topic_2"]] += 1

        if row["reuse"] == "conceptual":
            data["c"][row["topic_0"]] += 1
            data["c"][row["topic_1"]] += 1
            data["c"][row["topic_2"]] += 1

        if row["reuse"] == "deployment":
            data["d"][row["topic_0"]] += 1
            data["d"][row["topic_1"]] += 1
            data["d"][row["topic_2"]] += 1

    print(data)


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

    # compute(gpt_df=gpt_df)
    compute_aa(aa_df)


if __name__ == "__main__":
    main()
