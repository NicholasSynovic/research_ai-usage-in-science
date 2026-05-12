import argparse
import logging
import sqlite3
from pathlib import Path

import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def query_database(db_path: Path) -> pd.DataFrame:
    # 1. Connect to the database in read-only mode
    db_uri = f"file:{db_path}?mode=ro"

    conn = sqlite3.connect(db_uri, uri=True)

    # 2. SQL Query extracting year from JSON and filtering via the View
    query = """
        SELECT
            ns.doi,
            a.megajournal,
            CAST(json_extract(oa.json_data, '$.publication_year') AS INTEGER) as year
        FROM
            natural_science_article_dois ns
        JOIN
            articles a ON ns.doi = a.doi
        JOIN
            openalex oa ON ns.doi = oa.doi
        WHERE
            oa.json_data IS NOT NULL
    """

    logger.info("Reading Natural Science DOIs and extracting years...")
    return pd.read_sql_query(query, conn)


def split_into_dfs_by_megajournal(df: pd.DataFrame) -> list[pd.DataFrame]:
    return [x[1] for x in df.groupby("megajournal")]


def sample_by_year(df: pd.DataFrame, random_state: int = 42) -> pd.DataFrame:
    dfs: list[pd.DataFrame] = []

    sampled_df = df.groupby(by="year")

    for _, _df in sampled_df:
        dfs.append(_df.sample(frac=0.10, random_state=random_state))

    return pd.concat(objs=dfs, ignore_index=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sample 10% of DOIs per year per megajournal."
    )
    parser.add_argument("--db", help="Path to your .sqlite3 database file", type=Path)
    parser.add_argument(
        "--out", default="sampled_10_percent.csv", help="Output filename"
    )

    args = parser.parse_args()

    df = query_database(db_path=args.db)

    dfs: list[pd.DataFrame] = []
    for _df in split_into_dfs_by_megajournal(df):
        dfs.append(sample_by_year(df=_df))

    pd.concat(objs=dfs, ignore_index=True).sort_values(
        by="year",
        ignore_index=True,
    ).to_csv(path_or_buf=args.out)
