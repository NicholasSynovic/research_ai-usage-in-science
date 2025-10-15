import json
from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from pandas import DataFrame, Series

from aius.db import DB


def get_data(db: DB) -> tuple[DataFrame, DataFrame]:
    plos_paper_openalex_metadata_sql_query: str = """
    SELECT
        plos_paper_openalex_metadata._id,
        plos_paper_openalex_metadata.plos_paper_id,
        plos_paper_openalex_metadata.json
    FROM plos_paper_openalex_metadata;
    """

    plos_natural_science_papers_sql_query: str = """
    SELECT
        plos_natural_science_papers.*
    FROM
        plos_natural_science_papers;
"""

    return (
        pandas.read_sql_query(
            sql=plos_paper_openalex_metadata_sql_query,
            con=db.engine,
            index_col="_id",
        ),
        pandas.read_sql_query(
            sql=plos_natural_science_papers_sql_query,
            con=db.engine,
            index_col="_id",
        ),
    )


def format_openalex_df(openalex_df: DataFrame) -> DataFrame:
    # Make the `json` column a Series[dict]
    openalex_df["json"] = openalex_df["json"].apply(json.loads)

    # Extract the `publication_year` value from the JSON and store in a new column
    openalex_df["year"] = openalex_df["json"].apply(lambda x: x["publication_year"])

    return openalex_df


def format_plos_natural_science_df(
    plos_ns_df: DataFrame,
    openalex_df: DataFrame,
) -> DataFrame:
    # Set plos_ns_df index to the plos_paper_id colum
    plos_ns_df = plos_ns_df.reset_index(names="_id").set_index(
        keys="plos_paper_id",
    )

    # Join on openalex_df
    plos_ns_df = plos_ns_df.join(other=openalex_df.copy(), on="plos_paper_id")

    return plos_ns_df


def compute_paper_counts_per_year(
    plos_ns_df: DataFrame,
    openalex_df: DataFrame,
) -> DataFrame:
    # Count all papers in OpenAlex per year
    oa_count: Series[int] = openalex_df.value_counts(subset="year").sort_index()
    oa_count.name = "All PLOS Papers"

    # Count all papers in PLOS Natural Science per year
    pns_count: Series[int] = plos_ns_df.value_counts(subset="year").sort_index()
    pns_count.name = "PLOS Natural Science Papers"

    return pandas.concat([pns_count, oa_count], axis=1).fillna(0).astype(int)


def plot(df: DataFrame) -> None:
    # Set seaborn style to the default
    sns.set_style(style="white")

    # Plot data
    ax = df.plot(
        kind="bar",
        stacked=True,
        # figsize=(8, 5),
        title="All PLOS Papers vs PLOS Natural Science\nPapers Per Year",
        color=["#ff7f0e", "#1f77b4"],  # optional custom colors
    )

    plt.xlabel(xlabel="Year")
    plt.xticks(rotation=0)
    plt.xticks()
    plt.ylabel(ylabel="Paper Count")
    plt.legend(title="")

    # Reorder legend (plos_ns first, oa second)
    handles, labels = ax.get_legend_handles_labels()
    order = ["PLOS Natural Science Papers", "All PLOS Papers"]
    order_idx = [labels.index(name) for name in order if name in labels]
    ax.legend([handles[i] for i in order_idx], [labels[i] for i in order_idx], title="")

    for i, container in enumerate(ax.containers):
        # Lower bar (plos_ns)
        if i == 0:
            ax.bar_label(
                container, label_type="edge", fmt="%d", fontsize=8, color="white"
            )
        # Top bar (oa)
        else:
            ax.bar_label(
                container, label_type="edge", fmt="%d", fontsize=8, color="black"
            )

    plt.tight_layout()
    plt.savefig("figD.pdf")


@click.command()
@click.option(
    "--db-path",
    required=True,
    help="Path to the database",
    type=lambda x: Path(x).resolve(),
)
def main(db_path: Path) -> None:
    db: DB = DB(db_path=db_path)

    openalex_df: DataFrame
    plos_ns_df: DataFrame
    openalex_df, plos_ns_df = get_data(db=db)

    openalex_df: DataFrame = format_openalex_df(openalex_df=openalex_df)

    plos_ns_df = format_plos_natural_science_df(
        plos_ns_df=plos_ns_df,
        openalex_df=openalex_df,
    )

    df: DataFrame = compute_paper_counts_per_year(
        plos_ns_df=plos_ns_df,
        openalex_df=openalex_df,
    )

    plot(df=df)


if __name__ == "__main__":
    main()
