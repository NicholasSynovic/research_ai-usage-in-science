from argparse import ArgumentParser, Namespace
from pathlib import Path

import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from pandas import DataFrame

from aius.db import DB

PROGRAM_NAME: str = "Total Nature and PLOS Natural Science Papers"
DB_HELP: str = "Path to database"
FIGURE_PATH: Path = Path("total_plos_nature_natural_science_papers.pdf").resolve()


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
        JOIN searches_to_papers sbt ON s._id = sbt.search_id
        WHERE sbt.paper_id IN (SELECT paper_id FROM ns_papers);
    """
    return pandas.read_sql_query(sql=sql_query, con=db.engine)


def compute(df: DataFrame) -> DataFrame:
    data: DataFrame = df["journal"].value_counts().to_frame().reset_index(drop=False)
    # Format data
    data["journal"] = (
        data["journal"]
        .str.upper()
        .str.replace(
            pat="NATURE",
            repl="Nature",
        )
    )

    return data


def plot(data: DataFrame) -> None:
    # Plot
    sns.barplot(data=data, x="journal", y="count")

    # Title
    plt.title(label=PROGRAM_NAME)

    # X axis
    plt.xlabel(xlabel="Journal")

    # Y axis
    plt.ylabel(ylabel="Natural Science Papers Captured")  # Set y axis labe

    # Add commas to y axis values
    current_values = plt.gca().get_yticks()
    plt.gca().set_yticklabels(["{:,.0f}".format(x) for x in current_values])

    # Add values to the tops of bars
    for i in range(len(data["journal"])):
        y_value: int = data["count"][i] + data["count"][i] * 0.01
        value: str = "{:,.0f}".format(data["count"][i])
        plt.text(x=i, y=y_value, s=value, ha="center")

    # Save figure
    plt.tight_layout()
    plt.savefig(FIGURE_PATH)


def main() -> None:
    # Get command line args
    ns: Namespace = cli()

    # Create DB instance
    db: DB = DB(db_path=ns.db)

    # Get data from database
    df: DataFrame = get_data(db=db)

    # Compute data
    data: DataFrame = compute(df=df)

    # Plot data
    plot(data=data)


if __name__ == "__main__":
    main()
