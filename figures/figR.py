from json import loads
from pathlib import Path

import click
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.ticker import FuncFormatter
from pandas import DataFrame, Series
from sqlalchemy import Engine, create_engine

DB_PATH: Path = Path("../data/aius_12-17-2025.db").resolve()

FIELD: list[str] = [
    "Agricultural and Biological Sciences",
    "Biochemistry, Genetics and Molecular Biology",
    "Chemistry",
    "Earth and Planetary Sciences",
    "Environmental Science",
    "Immunology and Microbiology",
    "Neuroscience",
    "Physics and Astronomy",
]
SUPTITLE_FONT_SIZE: int = 24
TITLE_FONT_SIZE: int = 22
XY_LABEL_FONT_SIZE: int = 20
XY_TICK_FONT_SIZE: int = 18
OTHER_FONT_SIZE: int = XY_TICK_FONT_SIZE


def get_papers_per_journal(db: Engine) -> DataFrame:
    sql: str = "SELECT doi, megajournal FROM articles"
    return pd.read_sql(sql=sql, con=db)


def get_papers(db: Engine) -> DataFrame:
    sql: str = """
SELECT
    udl.doi, oa.topic_0, oa.topic_1, oa.topic_2, oa.json_data
FROM
    uses_dl_analysis udl
JOIN
    openalex oa
ON
    oa.doi = udl.doi
"""
    return pd.read_sql(sql=sql, con=db)


def create_data(df: DataFrame) -> DataFrame:
    top_fields: list[str] = [
        "Biochemistry, Genetics and Molecular Biology",
        "Neuroscience",
        "Environmental Science",
        "Other",
    ]

    data: dict[str, list[str | int]] = {"year": [], "field": []}

    row: Series
    for _, row in df.iterrows():
        topics: list[str] = [
            str(row["topic_0"]),
            str(row["topic_1"]),
            str(row["topic_2"]),
        ]
        json: dict = loads(str(row["json_data"]))
        for topic in topics:
            if json["publication_year"] > 2016:
                data["year"].append(json["publication_year"])
                data["field"].append(topic)

    data_df = DataFrame(data=data)
    data_df["field"] = np.where(
        data_df["field"].isin(top_fields),
        data_df["field"],
        "Other",
    )
    data_df = data_df[data_df["field"].isin(top_fields)]
    counts: Series = data_df.value_counts()

    counts_df = counts.reset_index()
    counts_df.columns = ["year", "field", "count"]

    return counts_df


def plot(df: DataFrame, output_path: Path) -> None:
    top_fields: list[str] = [
        "Biochemistry, Genetics and Molecular Biology",
        "Neuroscience",
        "Environmental Science",
        "Other",
    ]
    panel_labels: list[str] = ["(A)", "(B)", "(C)", "(D)"]

    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(15, 12), sharey=True)
    flat_axes = axes.flatten()
    max_count = df["count"].max()

    for index, field in enumerate(top_fields):
        ax = flat_axes[index]
        panel_data: DataFrame = df.loc[df["field"] == field]

        sns.barplot(
            data=panel_data,
            x="year",
            y="count",
            ax=ax,
        )

        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}"))
        ax.set_ylim(0, max_count * 1.15)
        ax.set_title(field, fontsize=TITLE_FONT_SIZE)
        ax.set_xlabel("Year", fontsize=XY_LABEL_FONT_SIZE)
        ax.set_ylabel("Paper Count", fontsize=XY_LABEL_FONT_SIZE)
        ax.tick_params(axis="both", labelsize=XY_TICK_FONT_SIZE)
        ax.tick_params(axis="x", rotation=45)

        if ax.get_legend() is not None:
            ax.get_legend().remove()

        for container in ax.containers:
            ax.bar_label(
                container,
                fmt="{:,.0f}",
                padding=3,
                fontsize=OTHER_FONT_SIZE,
            )

        ax.text(
            0.02,
            0.98,
            panel_labels[index],
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=TITLE_FONT_SIZE,
            fontweight="bold",
        )

    fig.suptitle(
        "Number Of Papers Using Deep Learning per Year",
        fontsize=SUPTITLE_FONT_SIZE,
    )
    fig.tight_layout()
    fig.savefig(output_path)


@click.command()
@click.option(
    "--db",
    "db_path",
    default=Path("../data/aius_12-17-2025.db").absolute(),
    type=click.Path(path_type=Path),
    show_default=True,
    help="Path to the SQLite database.",
)
@click.option(
    "--output",
    "output_path",
    default=Path("figR.pdf").absolute(),
    type=click.Path(path_type=Path),
    show_default=True,
    help="Output path for the plot.",
)
def main(db_path: Path, output_path: Path) -> None:
    db_path = db_path.absolute()
    output_path = output_path.absolute()
    db: Engine = create_engine(url=f"sqlite:///{db_path}")

    papers: DataFrame = get_papers(db=db)

    df: DataFrame = create_data(df=papers)

    plot(df=df, output_path=output_path)


if __name__ == "__main__":
    main()
