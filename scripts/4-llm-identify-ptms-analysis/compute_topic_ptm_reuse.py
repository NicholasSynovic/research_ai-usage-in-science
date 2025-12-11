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
    data: dict[str, list[str | None]] = defaultdict(list)

    row: Series
    for _, row in df.iterrows():
        match row["classification"]:
            case "adaptation_reuse":
                data["adaptation"].append(row["topic_0"])
                data["adaptation"].append(row["topic_1"])
                data["adaptation"].append(row["topic_2"])
                data["conceptual"].append(None)
                data["conceptual"].append(None)
                data["conceptual"].append(None)
                data["deployment"].append(None)
                data["deployment"].append(None)
                data["deployment"].append(None)
            case "conceptual_reuse":
                data["conceptual"].append(row["topic_0"])
                data["conceptual"].append(row["topic_1"])
                data["conceptual"].append(row["topic_2"])
                data["adaptation"].append(None)
                data["adaptation"].append(None)
                data["adaptation"].append(None)
                data["deployment"].append(None)
                data["deployment"].append(None)
                data["deployment"].append(None)
            case "deployment_reuse":
                data["deployment"].append(row["topic_0"])
                data["deployment"].append(row["topic_1"])
                data["deployment"].append(row["topic_2"])
                data["adaptation"].append(None)
                data["adaptation"].append(None)
                data["adaptation"].append(None)
                data["conceptual"].append(None)
                data["conceptual"].append(None)
                data["conceptual"].append(None)

    df: DataFrame = DataFrame(data=data)

    print(df[df["deployment"] == "Environmental Science"].shape[0])


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
    aa_df: DataFrame = get_aa(db=db).reset_index(names="_id")

    df: DataFrame = pandas.read_json(path_or_buf=i)

    df = df.join(other=aa_df, on="_id", rsuffix="aa")

    # df["result"] = df["result"].astype(dtype=bool)

    # df = df[df["result"] == True]
    # df = df.join(other=aa_df)

    compute(df=df)


if __name__ == "__main__":
    main()
