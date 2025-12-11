import json
from collections import defaultdict
from pathlib import Path
from pprint import pprint as print

import click
import pandas
from pandas import DataFrame, Series
from pandas.core.groupby import DataFrameGroupBy

from aius.db.db import DB


def get_aa(db: DB) -> DataFrame:
    sql_query: str = """
    SELECT
        plos_natural_science_papers.*,
        plos_paper_openalex_metadata.json
    FROM
        plos_natural_science_papers
    JOIN
        plos_paper_openalex_metadata
    ON
        plos_natural_science_papers.plos_paper_id = plos_paper_openalex_metadata.plos_paper_id;
    """

    return pandas.read_sql_query(sql=sql_query, con=db.engine, index_col="_id")


def compute(df: DataFrame) -> None:
    df_data: dict[str, list[int]] = defaultdict(list)
    data: dict[int, tuple[int, int, int]] = {}

    row: Series
    for _, row in df.iterrows():
        match row["classification"]:
            case "adaptation_reuse":
                df_data["year"].append(row["year"])
                df_data["conceptual"].append(0)
                df_data["adaptation"].append(1)
                df_data["deployment"].append(0)
            case "conceptual_reuse":
                df_data["year"].append(row["year"])
                df_data["conceptual"].append(1)
                df_data["adaptation"].append(0)
                df_data["deployment"].append(0)
            case "deployment_reuse":
                df_data["year"].append(row["year"])
                df_data["conceptual"].append(0)
                df_data["adaptation"].append(0)
                df_data["deployment"].append(1)

    reuse_df: DataFrame = DataFrame(data=df_data)
    dfgb: DataFrameGroupBy = reuse_df.groupby(by="year")

    year: int
    _df: DataFrame
    for year, _df in dfgb:
        data[year] = (
            _df["conceptual"].sum(),
            _df["adaptation"].sum(),
            _df["deployment"].sum(),
        )

    print(DataFrame(data=data).T)


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
    aa_df["year"] = aa_df["json"].apply(lambda x: json.loads(s=x)["publication_year"])

    df: DataFrame = pandas.read_json(path_or_buf=i).set_index(keys="_id")
    df = df.join(other=aa_df)

    compute(df=df)


if __name__ == "__main__":
    main()
