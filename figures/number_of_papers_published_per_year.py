from argparse import ArgumentParser, Namespace
from pathlib import Path
from textwrap import fill

import matplotlib.pyplot as plt
import numpy as np
import pandas
import seaborn as sns
from pandas import DataFrame
from pandas.core.groupby import DataFrameGroupBy

import aius
from aius.db import DB

PROGRAM_NAME: str = "Number of Papers Published Per Year"
DB_HELP: str = "Path to database"
FIGURE_PATH: Path = Path("number_of_papers_published_per_year.pdf").resolve()


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
        SELECT s.year, s.journal, sbt.paper_id FROM searches s
	    JOIN searches_to_papers sbt WHERE sbt.search_id = s._id;
    """
    return pandas.read_sql_query(sql=sql_query, con=db.engine)


def compute(df: DataFrame) -> DataFrame:
    df_list: list[DataFrame] = []

    # Group data by journal
    df_gb: DataFrameGroupBy = df.groupby(by="journal")

    # For each group, extract compute values
    _df: DataFrame
    journal: str
    for journal, _df in df_gb:
        datum: DataFrame = _df["year"].value_counts().to_frame().reset_index()

        if journal == "plos":
            datum["Journal"] = "PLOS"
        else:
            datum["Journal"] = "Nature"

        df_list.append(datum)

    data: DataFrame = pandas.concat(objs=df_list, ignore_index=True)

    return data.sort_values(by="year", ignore_index=True, ascending=True)


def plot(data: DataFrame) -> None:
    # Plot
    ax = sns.barplot(data=data, x="year", y="count", hue="Journal")

    # Title
    plt.title(label=PROGRAM_NAME)

    # X axis
    plt.xlabel(xlabel="Year")
    # plt.xticks(size="x-small")

    # Y axis
    plt.ylabel(ylabel="Number of Papers Published")  # Set y axis labe

    # Add commas to y axis values
    current_values = plt.gca().get_yticks()
    plt.gca().set_yticklabels(["{:,.0f}".format(x) for x in current_values])

    # Add values to the tops of bars
    for p in ax.patches:
        height = p.get_height()

        if height == 0:
            continue

        if not np.isnan(height):  # skip empty bars
            ax.text(
                x=p.get_x() + p.get_width() / 2,  # center of bar
                y=height + (height * 0.001),  # just above bar
                s=f"{int(height):,}",  # formatted text
                ha="center",
                va="bottom",
                size="x-small",
            )

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
