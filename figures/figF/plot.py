from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from pandas import DataFrame

from aius.db import DB


def get_data(db: DB) -> DataFrame:
    sql_query: str = """
    SELECT
        plos_natural_science_paper_content.raw_jats_xml_token_count,
        plos_natural_science_paper_content.formatted_jats_xml_token_count,
        plos_natural_science_paper_content.raw_md_token_count,
        plos_natural_science_paper_content.formatted_md_token_count
    FROM plos_natural_science_paper_content;
    """

    return pandas.read_sql_query(sql=sql_query, con=db.engine)


def preprocess_data(df: DataFrame) -> DataFrame:
    df = df.rename(
        columns={
            "raw_jats_xml_token_count": "JATS XML",
            "formatted_jats_xml_token_count": "Formatted JATS XML",
            "raw_md_token_count": "Markdown",
            "formatted_md_token_count": "Formatted Markdown",
        }
    )

    df = df[sorted(df.columns, key=lambda col: df[col].max(), reverse=True)]
    return df


def plot(df: DataFrame) -> None:
    sns.boxplot(data=df, showfliers=False)
    plt.title(label="Tokens per Document Format")
    plt.xlabel(xlabel="Document Format")
    plt.ylabel(ylabel="Token Count")

    # Compute summary stats
    summary = df.agg(
        [
            "min",
            "median",
            lambda s: s.quantile(0.75) + 1.5 * (s.quantile(0.75) - s.quantile(0.25)),
        ]
    ).T
    summary.columns = ["min", "median", "q3"]

    # Annotate each box
    for i, (col, stats) in enumerate(summary.iterrows()):
        min_val, median_val, q3_val = stats["min"], stats["median"], stats["q3"]

        plt.text(
            i,
            q3_val,
            f"{int(q3_val):,}",
            ha="center",
            va="bottom",
            fontsize=8,
            color="black",
        )
        plt.text(
            i,
            median_val + 2000,
            f"{int(median_val):,}",
            ha="center",
            va="center",
            fontsize=8,
            color="white",
        )
        plt.text(
            i,
            min_val - 2000,
            f"{int(min_val):,}",
            ha="center",
            va="top",
            fontsize=8,
            color="black",
        )

    plt.tight_layout()
    plt.savefig("figF.pdf")


@click.command()
@click.option(
    "--db-path",
    help="Path to database",
    type=lambda x: Path(x).resolve(),
    required=True,
)
def main(db_path: Path) -> None:
    df: DataFrame = get_data(db=DB(db_path=db_path))

    df = preprocess_data(df=df)

    plot(df=df)


if __name__ == "__main__":
    main()
