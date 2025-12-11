import json
from collections import defaultdict
from pathlib import Path
from pprint import pprint as print

import click
import pandas
from pandas import DataFrame, Series
from pandas.core.groupby import DataFrameGroupBy

from aius.db.db import DB


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
    df["reuse"] = df["ptm_name_reuse_type"].apply(lambda x: json.loads(x)["reuse"])

    return df


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

    return df.join(other=aa_df, rsuffix="aa")


def compute_gpt(gpt_df: DataFrame, aa_df: DataFrame) -> None:
    data: dict[int, dict[str, int]] = defaultdict(dict)

    gpt_df = gpt_df[["reuse", "year"]]
    gpt_df = gpt_df.explode(column="reuse")

    dfgb: DataFrameGroupBy = gpt_df.groupby(by="year")
    year: int
    _df: DataFrame
    for year, _df in dfgb:
        counts: Series = _df["reuse"].value_counts()

        for x, y in counts.items():
            data[year][x] = y

        # data[year].append(counts["reuse"])

    print(dict(data))


def compute_aa(aa_df: DataFrame) -> None:
    data: dict[int, dict[str, int]] = defaultdict(dict)

    aa_df["reuse"] = aa_df["ptm_name_reuse_type"].apply(
        lambda x: json.loads(s=x)["reuse"]
    )
    aa_df = aa_df[aa_df["reuse"].str.len() != 0]
    aa_df = aa_df.explode(column="reuse")
    aa_df = aa_df[["reuse", "year"]]

    dfgb: DataFrameGroupBy = aa_df.groupby(by="year")
    year: int
    _df: DataFrame
    for year, _df in dfgb:
        counts: Series = _df["reuse"].value_counts()

        for x, y in counts.items():
            data[year][x] = y

        # data[year].append(counts["reuse"])

    print(dict(data))


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

    compute_gpt(gpt_df, aa_df)
    compute_aa(aa_df=aa_df)

    pass


if __name__ == "__main__":
    main()
