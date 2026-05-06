from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter
from pandas import DataFrame
from sqlalchemy import Engine, create_engine

SUPTITLE_FONT_SIZE: int = 24
TITLE_FONT_SIZE: int = 20
XY_LABEL_FONT_SIZE: int = 18
XY_TICK_FONT_SIZE: int = 15
OTHER_FONT_SIZE: int = 14

MEGAJOURNALS: list[str] = ["BMJ", "F1000", "FrontiersIn", "PLOS"]


def get_keyword_counts_per_journal(db: Engine) -> DataFrame:
    sql: str = """
    SELECT
        megajournal,
        search_keyword,
        COUNT(*) AS count
    FROM
        searches
    GROUP BY
        megajournal,
        search_keyword
    ;
    """
    return pd.read_sql(sql=sql, con=db)


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
    oa.cited_by_count > 0;
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


def get_jats_per_journal(db: Engine) -> DataFrame:
    sql: str = """
SELECT
    a.doi,
    a.megajournal
FROM
    articles a
JOIN
    jats j ON a.doi = j.doi;
"""
    return pd.read_sql(sql=sql, con=db)


def create_bar_data(
    df1: DataFrame, df2: DataFrame, df3: DataFrame, df4: DataFrame
) -> DataFrame:
    data: dict[str, list[int | str]] = {
        "journal": MEGAJOURNALS,
        "Total Papers": [],
        "Papers With Citations": [],
        "Natural Science Papers": [],
        "JATS XML Papers": [],
    }

    def _run(key: str, df: DataFrame) -> None:
        counts = df["megajournal"].value_counts()
        for journal in MEGAJOURNALS:
            data[key].append(int(counts.get(journal, 0)))

    _run("Total Papers", df1)
    _run("Papers With Citations", df2)
    _run("Natural Science Papers", df3)
    _run("JATS XML Papers", df4)

    return DataFrame(data=data)


def _plot_pie_chart(ax: plt.Axes, df: DataFrame, journal: str) -> None:
    journal_df = df[df["megajournal"] == journal].copy()
    if journal_df.empty:
        ax.set_axis_off()
        ax.set_title(f"{journal} (no data)", fontsize=TITLE_FONT_SIZE)
        return

    labels = journal_df["search_keyword"].tolist()
    counts = journal_df["count"].astype(int).tolist()
    total = sum(counts)
    pct_labels = [f"{value / total:.0%}" for value in counts]
    colors = [KEYWORD_COLORS[label] for label in labels]

    ax.pie(
        counts,
        labels=pct_labels,
        colors=colors,
        startangle=90,
        counterclock=False,
        textprops={"fontsize": OTHER_FONT_SIZE},
    )
    ax.set_title(journal, fontsize=TITLE_FONT_SIZE)


def _get_shared_pie_legend(df: DataFrame) -> list[str]:
    keywords = df["search_keyword"].dropna().astype(str).unique().tolist()
    return sorted(keywords)


KEYWORD_COLORS: dict[str, str] = {}


def plot(pie_df: DataFrame, bar_df: DataFrame, output_path: Path) -> None:
    global KEYWORD_COLORS

    df_long = bar_df.melt(
        id_vars="journal",
        value_vars=[
            "Total Papers",
            "Papers With Citations",
            "Natural Science Papers",
            # "JATS XML Papers",
        ],
        var_name="category",
        value_name="count",
    )

    shared_keywords = _get_shared_pie_legend(pie_df)
    palette = sns.color_palette("tab20", n_colors=max(len(shared_keywords), 1))
    KEYWORD_COLORS = {
        keyword: palette[index % len(palette)]
        for index, keyword in enumerate(shared_keywords)
    }

    fig = plt.figure(figsize=(24, 12))
    gs = GridSpec(
        2, 5, figure=fig, width_ratios=[0.9, 1, 1, 1, 1], height_ratios=[1.2, 1.2]
    )

    legend_ax = fig.add_subplot(gs[0, 0])
    legend_ax.set_axis_off()
    legend_handles = [
        Patch(facecolor=KEYWORD_COLORS[keyword], label=keyword)
        for keyword in shared_keywords
    ]
    legend_ax.legend(
        handles=legend_handles,
        title="Keyword",
        loc="center left",
        fontsize=OTHER_FONT_SIZE,
        title_fontsize=OTHER_FONT_SIZE,
        frameon=True,
    )

    for index, journal in enumerate(MEGAJOURNALS):
        ax = fig.add_subplot(gs[0, index + 1])
        _plot_pie_chart(ax=ax, df=pie_df, journal=journal)

    ax = fig.add_subplot(gs[1, :])
    sns.barplot(
        data=df_long,
        x="journal",
        y="count",
        hue="category",
        ax=ax,
    )
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_ylim(0, df_long["count"].max() * 1.15)
    ax.set_title("Filtering Process", fontsize=TITLE_FONT_SIZE)
    ax.set_xlabel("Megajournal", fontsize=XY_LABEL_FONT_SIZE)
    ax.set_ylabel("Paper Count", fontsize=XY_LABEL_FONT_SIZE)
    ax.tick_params(axis="both", labelsize=XY_TICK_FONT_SIZE)
    ax.legend(title="", fontsize=OTHER_FONT_SIZE)

    for container in ax.containers:
        ax.bar_label(container, fmt="{:,.0f}", padding=3, fontsize=OTHER_FONT_SIZE)

    fig.suptitle(
        "Keyword Returns and Filtering by Megajournal", fontsize=SUPTITLE_FONT_SIZE
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(output_path)


@click.command()
@click.option(
    "--db",
    "db_path",
    default=Path("../data/aius.3-18-2026.db").resolve(),
    type=click.Path(path_type=Path),
    show_default=True,
    help="Path to the SQLite database.",
)
@click.option(
    "--output",
    "output_path",
    default=Path("figQ_update.pdf").absolute(),
    type=click.Path(path_type=Path),
    show_default=True,
    help="Output path for the plot.",
)
def main(db_path: Path, output_path: Path) -> None:
    db_path = db_path.absolute()
    output_path = output_path.absolute()
    db: Engine = create_engine(url=f"sqlite:///{db_path}")

    pie_df: DataFrame = get_keyword_counts_per_journal(db=db)
    papers: DataFrame = get_papers_per_journal(db=db)
    papers_with_citations: DataFrame = get_papers_with_citations_per_journal(db=db)
    natural_science_papers: DataFrame = get_natural_science_papers_per_journal(db=db)
    jats_papers: DataFrame = get_jats_per_journal(db=db)

    bar_df: DataFrame = create_bar_data(
        df1=papers,
        df2=papers_with_citations,
        df3=natural_science_papers,
        df4=jats_papers,
    )

    plot(pie_df=pie_df, bar_df=bar_df, output_path=output_path)


if __name__ == "__main__":
    main()
