from argparse import ArgumentParser, Namespace
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import pandas
import seaborn as sns
import upsetplot
from pandas import DataFrame, Series

from aius.db import DB

PROGRAM_NAME: str = "Breakdown Of PLOS Keyword Searches"
DB_HELP: str = "Path to database"
FIGURE_PATH: Path = Path("breakdown_of_plos_keyword_searches.pdf").resolve()


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
        SELECT stp.*, s.keyword FROM searches_to_papers stp
        JOIN searches s ON stp.search_id = s._id
        WHERE stp.search_id < 164;
    """

    return pandas.read_sql_query(sql=sql_query, con=db.engine, index_col="_id")


def create_upset_data(df: DataFrame) -> DataFrame:
    data: dict[str, list] = defaultdict(list)

    keywords: list[str] = [
        '"Model Weights"',
        '"Deep Neural Network"',
        '"Deep Learning"',
        '"HuggingFace"',
        '"Model Checkpoint"',
        '"Pre-Trained Model"',
        '"Hugging Face"',
    ]

    unique_paper_ids: list[int] = sorted(df["paper_id"].unique().tolist())

    idx: int
    for idx in unique_paper_ids:
        rows: DataFrame = df[df["paper_id"] == idx]
        classes: set[str] = set(rows["keyword"].to_list())

        keyword: str
        for keyword in keywords:
            data[keyword].append(keyword in classes)

    return upsetplot.from_indicators(
        indicators=keywords,
        data=DataFrame(
            data=data,
        ),
    )


def plot(df: DataFrame) -> None:
    upsp: upsetplot.UpSet = upsetplot.UpSet(data=df, show_counts=True)
    upsp.plot()
    plt.title(label="PLOS Documents Returned From Search Results Per Keyword")
    plt.xlabel(xlabel="Keyword(s)")
    plt.ylabel(ylabel="Document Count")
    plt.savefig(FIGURE_PATH)


def main() -> None:
    # Get command line arguments
    args: Namespace = cli()

    # Connect to the database
    db: DB = DB(db_path=args.db)

    # Get the data
    df: DataFrame = get_data(db=db)

    # Create UpSet data
    # https://doi.org/10.1109/TVCG.2014.2346248
    upset_df: DataFrame = create_upset_data(df=df)

    # Plot UpSet data
    plot(df=upset_df)


if __name__ == "__main__":
    sns.set_theme()

    main()
