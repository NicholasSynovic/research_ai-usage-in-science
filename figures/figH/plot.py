from pathlib import Path

import click
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame
from sqlalchemy import text
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.sql.elements import TextClause

from aius.db.db import DB


# Get the number of PLOS papers
def get_total_plos_paper_count(db: DB) -> int:
    sql_query: TextClause = text(
        text="SELECT COUNT(DISTINCT stp.paper_id) FROM searches_to_papers stp WHERE stp.search_id < 165;"
    )
    with db.engine.connect() as connection:
        result: CursorResult = connection.execute(statement=sql_query)
        connection.close()
    return int(result.first()[0])


# Get the number of PLOS papers indexed by OpenAlex
def get_oa_indexed_plos_paper_count(db: DB) -> int:
    sql_query: TextClause = text(
        text="SELECT COUNT(DISTINCT o.paper_id) FROM openalex AS o JOIN searches_to_papers AS sp ON o.paper_id = sp.paper_id WHERE sp.search_id < 165;"
    )
    with db.engine.connect() as connection:
        result: CursorResult = connection.execute(statement=sql_query)
        connection.close()
    return int(result.first()[0])


# Get the number of PLOS papers indexed by OpenAlex with more than one citation
def get_oa_indexed_plos_papers_w_ciations_count(db: DB) -> int:
    sql_query: TextClause = text(
        text="SELECT COUNT(DISTINCT o.paper_id) FROM openalex AS o JOIN searches_to_papers AS sp ON o.paper_id = sp.paper_id WHERE sp.search_id < 165 AND o.cited_by_count > 0;"
    )
    with db.engine.connect() as connection:
        result: CursorResult = connection.execute(statement=sql_query)
        connection.close()
    return int(result.first()[0])


# Get the number of Natural Sciece PLOS papers indexed by OpenAlex with more than one citation
def get_ns_plos_papers_w_ciations_count(db: DB) -> int:
    sql_query: TextClause = text(
        text="SELECT COUNT(DISTINCT ns.paper_id) FROM ns_papers AS ns JOIN papers AS p ON ns.paper_id = p._id JOIN openalex AS o ON p._id = o.paper_id JOIN searches_to_papers AS sp ON p._id = sp.paper_id WHERE o.cited_by_count > 1 AND sp.search_id < 165;"
    )
    with db.engine.connect() as connection:
        result: CursorResult = connection.execute(statement=sql_query)
        connection.close()
    return int(result.first()[0])


def plot(df: DataFrame) -> None:
    sns.barplot(data=df)
    plt.title(label="Number Of Papers per Filtering Criteria")
    plt.ylabel(ylabel="Number Of Papers")
    plt.xlabel(xlabel="Filtering Criteria")
    plt.tight_layout()
    plt.savefig("figH.pdf")


@click.command()
@click.option(
    "-i",
    "--input-fp",
    required=True,
    type=lambda x: Path(x).resolve(),
    help="Path to AIUS database file",
)
def main(input_fp: Path) -> None:
    db: DB = DB(db_path=input_fp)

    plos_paper_count: int = get_total_plos_paper_count(db=db)
    oa_indexed_count: int = get_oa_indexed_plos_paper_count(db=db)
    oa_plos_w_citations_count: int = get_oa_indexed_plos_papers_w_ciations_count(db=db)
    ns_papers_count: int = get_ns_plos_papers_w_ciations_count(db=db)

    data: dict[str, list[int]] = {
        "PLOS": [plos_paper_count],
        "OpenAlex": [oa_indexed_count],
        "Cited": [oa_plos_w_citations_count],
        "Natural Science": [ns_papers_count],
    }

    df: DataFrame = DataFrame(data=data)
    plot(df=df)
    print(df)


if __name__ == "__main__":
    main()
