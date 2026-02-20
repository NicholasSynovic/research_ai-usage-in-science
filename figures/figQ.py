from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.ticker import FuncFormatter
from pandas import DataFrame, Series
from sqlalchemy import Engine, create_engine

SUPTITLE_FONT_SIZE: int = 24
TITLE_FONT_SIZE: int = 22
XY_LABEL_FONT_SIZE: int = 20
XY_TICK_FONT_SIZE: int = 18
OTHER_FONT_SIZE: int = XY_TICK_FONT_SIZE


def get_papers_per_journal(db: Engine) -> DataFrame:
    sql: str = "SELECT doi, megajournal FROM articles"
    return pd.read_sql(sql=sql, con=db)


def get_papers_with_citations_per_journal(db: Engine) -> DataFrame:
    sql: str = """
SELECT
    oa.doi, a.megajournal
FROM
    articles a
JOIN
    openalex oa
ON
    oa.doi == a.doi
WHERE
    json_extract(oa.json_data, '$.cited_by_count') > 0;
"""
    return pd.read_sql(sql=sql, con=db)


def get_natural_science_papers_per_journal(db: Engine) -> DataFrame:
    sql: str = """
SELECT
    ns.doi, a.megajournal
FROM
    articles a
JOIN
    natural_science_article_dois ns
ON
    ns.doi == a.doi;
"""
    return pd.read_sql(sql=sql, con=db)


def create_data(df1: DataFrame, df2: DataFrame, df3: DataFrame) -> DataFrame:
    data: dict[str, list[str | int]] = {
        "journal": ["BMJ", "F1000", "FrontiersIn", "PLOS"],
        "Total Papers": [],
        "Papers With Citations": [],
        "Natural Science Papers": [],
    }

    def _run(key: str, df: DataFrame) -> None:
        counts: Series = df["megajournal"].value_counts()
        data[key].append(counts["BMJ"])
        data[key].append(counts["F1000"])
        data[key].append(counts["FrontiersIn"])
        data[key].append(counts["PLOS"])

    _run("Total Papers", df1)
    _run("Papers With Citations", df2)
    _run("Natural Science Papers", df3)

    return DataFrame(data=data)


def plot(df: DataFrame, output_path: Path) -> None:
    # Convert wide → long format
    df_long = df.melt(
        id_vars="journal",
        value_vars=[
            "Total Papers",
            "Papers With Citations",
            "Natural Science Papers",
        ],
        var_name="category",
        value_name="count",
    )

    # Plot grouped bar chart
    plt.figure(figsize=(12, 9))
    ax = sns.barplot(
        data=df_long,
        x="journal",
        y="count",
        hue="category",
        # log_scale=True,
    )

    # ---- Y-AXIS: commas + headroom ----
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_ylim(0, df_long["count"].max() * 1.15)  # 15% headroom

    plt.suptitle(t="Paper Counts by Megajournal", fontsize=SUPTITLE_FONT_SIZE)
    plt.title(
        label="17,511 papers; 13,815 with citations; 4,384 natural science",
        fontsize=TITLE_FONT_SIZE,
    )
    plt.xlabel("Megajournal", fontsize=XY_LABEL_FONT_SIZE)
    plt.ylabel("Paper Count", fontsize=XY_LABEL_FONT_SIZE)
    plt.yticks(fontsize=XY_TICK_FONT_SIZE)
    plt.xticks(fontsize=XY_TICK_FONT_SIZE)
    plt.legend(title="", fontsize=OTHER_FONT_SIZE)

    # ---- ADD VALUE LABELS ----
    for container in ax.containers:
        ax.bar_label(
            container,
            fmt="{:,.0f}",
            padding=3,
            fontsize=OTHER_FONT_SIZE,
        )

    plt.tight_layout()
    plt.savefig(output_path)


@click.command()
@click.option(
    "--db",
    "db_path",
    default=Path("../data/aius_12-17-2025.db").resolve(),
    type=click.Path(path_type=Path),
    show_default=True,
    help="Path to the SQLite database.",
)
@click.option(
    "--output",
    "output_path",
    default=Path("figQ.pdf").absolute(),
    type=click.Path(path_type=Path),
    show_default=True,
    help="Output path for the plot.",
)
def main(db_path: Path, output_path: Path) -> None:
    db_path = db_path.absolute()
    output_path = output_path.absolute()
    db: Engine = create_engine(url=f"sqlite:///{db_path}")

    papers: DataFrame = get_papers_per_journal(db=db)
    papers_with_citations: DataFrame = get_papers_with_citations_per_journal(db=db)
    natural_science_papers: DataFrame = get_natural_science_papers_per_journal(db=db)

    df: DataFrame = create_data(
        df1=papers,
        df2=papers_with_citations,
        df3=natural_science_papers,
    )

    plot(df=df, output_path=output_path)


if __name__ == "__main__":
    main()
