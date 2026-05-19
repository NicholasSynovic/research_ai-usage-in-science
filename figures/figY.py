from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter
from pandas import DataFrame
from sqlalchemy import Engine, create_engine

SUPTITLE_FONT_SIZE: int = 24
TITLE_FONT_SIZE: int = 22
XY_LABEL_FONT_SIZE: int = 20
XY_TICK_FONT_SIZE: int = 18
OTHER_FONT_SIZE: int = XY_TICK_FONT_SIZE
DL_LABEL: str = "DL Usage"
NO_DL_LABEL: str = "No DL Usage"
FIGSIZE: tuple[float, float] = (12.8, 9.6)


def load_year_counts(db: Engine) -> DataFrame:
    sql: str = """
SELECT
    CAST(json_extract(oa.json_data, '$.publication_year') AS INTEGER) AS publication_year,
    COUNT(ns.doi) AS ns_article_count,
    COUNT(CASE WHEN ns.doi IS NULL THEN 1 END) AS openalex_only_count
FROM
    openalex oa
LEFT JOIN
    natural_science_article_dois ns
ON
    oa.doi == ns.doi
GROUP BY
    publication_year
ORDER BY
    publication_year DESC;
"""
    df: DataFrame = pd.read_sql(sql=sql, con=db)

    return df[df["publication_year"] < 2026]


def plot_counts(df: DataFrame, output_path: Path) -> None:
    if df.empty:
        raise ValueError("No classified papers available for plotting.")

    min_year: int = int(df["publication_year"].min())
    max_year: int = int(df["publication_year"].max())
    years: list[int] = list(range(min_year, max_year + 1))

    plot_df: DataFrame = df.copy()
    plot_df = plot_df.dropna(subset=["publication_year"])
    plot_df = plot_df.assign(publication_year=plot_df["publication_year"].astype(int))
    plot_df = plot_df.sort_values(by="publication_year")

    fig, ax = plt.subplots(figsize=FIGSIZE)

    red_bars = ax.bar(
        plot_df["publication_year"],
        plot_df["openalex_only_count"],
        # bottom=plot_df["ns_article_count"],
        color="#C44E52",
        label="OpenAlex only",
    )
    blue_bars = ax.bar(
        plot_df["publication_year"],
        plot_df["ns_article_count"],
        color="#4C78A8",
        label="Natural science articles",
    )

    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_xlabel("Year", fontsize=XY_LABEL_FONT_SIZE)
    ax.set_ylabel("Count", fontsize=XY_LABEL_FONT_SIZE)
    plt.suptitle(
        "Natural Science Papers Published per Year", fontsize=SUPTITLE_FONT_SIZE
    )

    ns_total: int = int(df["ns_article_count"].sum())
    openalex_only_total: int = int(df["openalex_only_count"].sum())
    ax.set_title(
        f"{ns_total:,} Natural Science; {openalex_only_total:,} OpenAlex Only",
        fontsize=TITLE_FONT_SIZE,
        loc="center",
    )
    xticks: list[int] = years[::2]
    ax.set_xticks(xticks)
    ax.set_xticklabels([str(year) for year in xticks], rotation=45)
    ax.tick_params(axis="both", labelsize=XY_TICK_FONT_SIZE)
    ax.legend(title="", fontsize=OTHER_FONT_SIZE)
    ax.grid(False)
    ax.set_axisbelow(True)

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


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
    default=Path("figY.pdf").absolute(),
    type=click.Path(path_type=Path),
    show_default=True,
    help="Output path for the stacked bar chart.",
)
def main(db_path: Path, output_path: Path) -> None:
    db_path = db_path.absolute()
    output_path = output_path.absolute()

    db: Engine = create_engine(url=f"sqlite:///{db_path}")

    counts: DataFrame = load_year_counts(db=db)
    plot_counts(df=counts, output_path=output_path)


if __name__ == "__main__":
    main()
