from argparse import ArgumentParser, Namespace
from pathlib import Path

import pandas
from pandas import DataFrame, Series

from aius.db import DB

PROGRAM_NAME: str = "Total PLOS and Nature Papers"
DB_HELP: str = "Path to database"


def cli() -> Namespace:
    parser: ArgumentParser = ArgumentParser(prog=PROGRAM_NAME)
    parser.add_argument(
        "-d",
        "--db",
        type=lambda x: Path(x).resolve(),
        required=True,
        help=DB_HELP,
    )
    return parser.parse_args()


def get_data(db: DB) -> DataFrame:
    sql_query: str = """
        SELECT s.journal, sbt.paper_id FROM searches s
        JOIN searches_to_papers sbt ON s._id = sbt.search_id;
    """
    return pandas.read_sql_query(sql=sql_query, con=db.engine)


def compute(df: DataFrame) -> Series:
    return df["journal"].value_counts()


def plot(data: Series) -> None:
    print(data)


def main() -> None:
    # Get command line args
    ns: Namespace = cli()

    # Create DB instance
    db: DB = DB(db_path=ns.db)

    # Get data from database
    df: DataFrame = get_data(db=db)

    # Compute data
    data: Series = compute(df=df)

    # Plot data
    plot(data=data)


if __name__ == "__main__":
    main()
