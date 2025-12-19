from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.ticker import FuncFormatter
from pandas import DataFrame, Series
from sqlalchemy import Engine, create_engine

DB_PATH: Path = Path("../data/aius_12-17-2025.db").resolve()


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


def plot(df: DataFrame) -> None:
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
    # plt.figure(figsize=(9, 5))
    ax = sns.barplot(
        data=df_long,
        x="journal",
        y="count",
        hue="category",
    )

    # ---- ADD VALUE LABELS ----
    for container in ax.containers:
        ax.bar_label(
            container,
            fmt="{:,.0f}",
            padding=3,
            fontsize=9,
        )

    # ---- Y-AXIS: commas + headroom ----
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}"))
    ymax = df_long["count"].max()
    ax.set_ylim(0, ymax * 1.15)  # 15% headroom

    plt.xlabel("Megajournal")
    plt.ylabel("Paper Count")
    plt.suptitle(t="Paper Counts by Megajournal")
    plt.title(label="17,511 papers; 13,815 with citations; 4,384 natural science")
    plt.legend(title="")
    plt.tight_layout()
    plt.savefig("figQ.pdf")


def main() -> None:
    db: Engine = create_engine(url=f"sqlite:///{DB_PATH}")

    papers: DataFrame = get_papers_per_journal(db=db)
    papers_with_citations: DataFrame = get_papers_with_citations_per_journal(db=db)
    natural_science_papers: DataFrame = get_natural_science_papers_per_journal(db=db)

    df: DataFrame = create_data(
        df1=papers,
        df2=papers_with_citations,
        df3=natural_science_papers,
    )

    plot(df=df)


if __name__ == "__main__":
    main()
