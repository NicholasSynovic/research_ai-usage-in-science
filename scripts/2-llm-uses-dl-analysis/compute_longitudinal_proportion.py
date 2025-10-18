import json
from pathlib import Path
from pprint import pprint as print

import click
import pandas
from pandas import DataFrame
from pandas.core.groupby import DataFrameGroupBy

from aius.db import DB


def get_db_df(db: DB) -> DataFrame:
    sql_query: str = """
    SELECT
        plos_natural_science_papers.*, plos_paper_openalex_metadata.json
    FROM
        plos_natural_science_papers
    JOIN
        plos_paper_openalex_metadata
    ON
        plos_natural_science_papers.plos_paper_id = plos_paper_openalex_metadata.plos_paper_id;
    """

    df: DataFrame = pandas.read_sql_query(
        sql=sql_query,
        con=db.engine,
        index_col="_id",
    )
    df["year"] = df["json"].apply(lambda x: json.loads(s=x)["publication_year"])

    return df


def compute_proportion_per_year(df: DataFrame) -> None:
    data: dict[int, tuple[int, int, float]] = {}
    dfgb: DataFrameGroupBy = df.groupby(by="year")

    year: int
    _df: DataFrame
    for year, _df in dfgb:
        size: int = _df.shape[0]

        _df = _df[_df["result"] == True]
        _df = _df[_df["prose"].str.len() >= 1]
        truthy_size: int = _df.shape[0]
        data[year] = (size, truthy_size, truthy_size / size * 100)

    print(data)


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

    df = df.join(other=db_df).sort_values(by="year")

    compute_proportion_per_year(df=df)


if __name__ == "__main__":
    main()
