from json import loads
from pathlib import Path

import matplotlib.pyplot as plt
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


def get_papers_per_journal(db: Engine) -> DataFrame:
    sql: str = "SELECT doi, megajournal FROM articles"
    return pd.read_sql(sql=sql, con=db)


def get_papers(db: Engine) -> DataFrame:
    sql: str = """
SELECT
    udl.doi, oa.topic_0, oa.topic_1, oa.topic_2, oa.json_data
FROM
    uses_ptms_analysis udl
JOIN
    openalex oa
ON
    oa.doi = udl.doi
"""
    return pd.read_sql(sql=sql, con=db)


def create_data(df: DataFrame) -> DataFrame:
    data: dict[str, list[str | int]] = {"year": [], "field": []}

    row: Series
    for _, row in df.iterrows():
        topics: list[str] = [row["topic_0"], row["topic_1"], row["topic_2"]]
        json: dict = loads(row["json_data"])
        for topic in topics:
            if json["publication_year"] > 2019:
                data["year"].append(json["publication_year"])
                data["field"].append(topic)

    df = DataFrame(data=data)
    df = df[
        df["field"].isin(
            [
                "Biochemistry, Genetics and Molecular Biology",
                "Agricultural and Biological Sciences",
                "Neuroscience",
            ]
        )
    ]
    counts: Series = df.value_counts()

    df = counts.reset_index()
    df.columns = ["year", "field", "count"]

    return df


def plot(df: DataFrame) -> None:
    plt.figure(figsize=(7, 6))

    ax = sns.barplot(
        data=df,
        x="year",
        y="count",
        hue="field",
    )

    # Add value labels
    for container in ax.containers:
        ax.bar_label(
            container,
            fmt="{:,.0f}",
            padding=3,
            fontsize=9,
        )

    # Formatting
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_ylim(0, df["count"].max() * 1.15)

    ax.set_xlabel("Year")
    ax.set_ylabel("Paper Count")
    ax.set_title("Paper Counts by Field and Year")
    ax.legend(title="Field", frameon=False)

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("figS.pdf")


def main() -> None:
    db: Engine = create_engine(url=f"sqlite:///{DB_PATH}")

    papers: DataFrame = get_papers(db=db)

    df: DataFrame = create_data(df=papers)

    plot(df=df)


if __name__ == "__main__":
    main()
