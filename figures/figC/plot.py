import warnings
from argparse import ArgumentParser, Namespace
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import pandas
import seaborn as sns
import upsetplot
from pandas import DataFrame

from aius.db import DB

warnings.filterwarnings(action="ignore")

PROGRAM_NAME: str = "Breakdown Of PLOS Keyword Searches"
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
    """
    Retrieve data concerning PLOS search results and associated keywords.

    This method constructs and executes an SQL query to fetch detailed
    information about searches performed on the PLOS platform, including
    metadata related to each search and its corresponding papers' DOIs (Digital
    Object Identifiers). The function is designed to facilitate comprehensive
    analysis or reporting by consolidating search-related data into a structured
    DataFrame.

    Parameters:
        db: DB
            A database connection object that provides access to the underlying
                SQL database. This parameter is essential for executing the SQL
                query against the relevant tables within the database.

    Returns:
        DataFrame:
            A pandas DataFrame containing rows of data extracted from the
                database, where each row corresponds to a specific PLOS search
                result along with associated keywords and DOI information linked
                to papers identified through these searches. The DataFrame's
                index column is set to "_id", facilitating easy identification
                and manipulation of records within the DataFrame.

    Notes:
        - The method constructs an SQL query that joins two tables:
            `plos_searches_to_paper_dois` and `plos_searches`, based on a common
            identifier (`search_id`). This join operation allows for the
            retrieval of detailed search metadata alongside associated paper DOI
            information.
        - The use of pandas' `read_sql_query` function simplifies the process of
            executing SQL queries and converting their results into DataFrame
            format, enhancing data manipulation capabilities within Python
            environments.
        - Indexing the resulting DataFrame by "_id" column optimizes operations
            that require quick access or sorting based on search identifiers,
            aligning with common practices in database management for efficient
            data retrieval and analysis.
    """
    sql_query: str = """
        SELECT
            plos_searches_to_paper_dois.*,
            plos_searches.keyword
        FROM plos_searches_to_paper_dois
        JOIN plos_searches
        ON
            plos_searches_to_paper_dois.plos_search_id = plos_searches._id;
    """

    return pandas.read_sql_query(sql=sql_query, con=db.engine, index_col="_id")


def create_upset_data(df: DataFrame) -> DataFrame:
    data: dict[str, list] = defaultdict(list)
    """
    Generate an UpSet plot data structure from a provided DataFrame

    This method facilitates the visualization of intersections among specified
    categories within the dataset. This method is particularly useful for
    analyzing and visualizing complex relationships between multiple categorical
    attributes (e.g., keywords) across various records in the DataFrame.

    Parameters:
        df: DataFrame
            A pandas DataFrame containing the raw data to be processed. The
            DataFrame must include at least two columns of interest:
            `plos_paper_id` for identifying unique records, and `keyword`
            listing associated categories or tags with each record. This method
            leverages these attributes to construct an UpSet plot, which is a
            powerful tool for visualizing the intersections among multiple sets.

    Returns:
        DataFrame:
            Although the primary output is an UpSet plot generated via
            `upsetplot.from_indicators`, this method returns a DataFrame
            representation of the data used in constructing the plot. This
            intermediate DataFrame includes all categories specified in the
            `keywords` list as columns, with each row corresponding to a unique
            `plos_paper_id` from the input DataFrame. The cell values indicate
            whether each keyword is present (True) or absent (False) for the
            respective paper ID.

    Notes:
        - The method begins by defining a fixed list of keywords relevant to the
            analysis. These categories are used as columns in the resulting
            UpSet plot, providing a structured way to compare their presence
            across different records.
        - It iterates over unique `plos_paper_id` values from the input DataFrame,
            extracting and categorizing each record's associated keywords into
            sets for comparison against predefined categories.
        - The final step involves using `upsetplot.from_indicators` to transform
            the categorized data into an UpSet plot format, which is inherently
            visual but can be represented in tabular form through the returned
            DataFrame. This representation aids in understanding the
            distribution and overlap of specified categories across different
            records.
        - The use of defaultdict ensures that all specified keywords are
            accounted for in the resulting dictionary structure, even if some
            keywords do not appear with certain `plos_paper_id` entries.
    """

    keywords: list[str] = [
        '"Model Weights"',
        '"Deep Neural Network"',
        '"Deep Learning"',
        '"HuggingFace"',
        '"Model Checkpoint"',
        '"Pre-Trained Model"',
        '"Hugging Face"',
    ]

    unique_paper_ids: list[int] = sorted(df["plos_paper_id"].unique().tolist())

    idx: int
    for idx in unique_paper_ids:
        rows: DataFrame = df[df["plos_paper_id"] == idx]
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
    plt.savefig("figC.pdf")


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

    # Print DataFrame information for the caption
    print("Total number of PLOS documents:", df.shape[0])
    print("Total unique PLOS documents:", df["plos_paper_id"].unique().shape[0])
    print("Total papers with 1 keyword:", upset_df[upset_df.sum(axis=1) == 1].shape[0])
    print(
        "Proportion of papers with 1 keyword:",
        upset_df[upset_df.sum(axis=1) == 1].shape[0]
        / df["plos_paper_id"].unique().shape[0],
    )

    # Plot UpSet data
    plot(df=upset_df)


if __name__ == "__main__":
    sns.set_theme()

    main()
