from json import loads
from pathlib import Path

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
        topics: list[str] = [row["topic_0"], row["topic_1"], row["topic_2"]]
        json: dict = loads(row["json_data"])
        for topic in topics:
            if json["publication_year"] > 2016:
                data["year"].append(json["publication_year"])
                data["field"].append(topic)

    df = DataFrame(data=data)
    df["field"] = np.where(df["field"].isin(top_fields), df["field"], "Other")
    df = df[df["field"].isin(top_fields)]
    counts: Series = df.value_counts()

    df = counts.reset_index()
    df.columns = ["year", "field", "count"]

    return df


def plot(df: DataFrame) -> None:
    plt.figure(figsize=(15, 12))

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
            fontsize=OTHER_FONT_SIZE,
        )

    # Formatting
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_ylim(0, df["count"].max() * 1.15)  # 15% headroom

    plt.title(
        "Number Of Papers Using Deep Learning per Year",
        fontsize=TITLE_FONT_SIZE,
    )
    # plt.title("Top three most prevelant fields presented", fontsize=MAX_FONT_SIZE-2,)
    plt.xlabel("Year", fontsize=XY_LABEL_FONT_SIZE)
    plt.ylabel("Paper Count", fontsize=XY_LABEL_FONT_SIZE)
    plt.yticks(fontsize=XY_TICK_FONT_SIZE)
    plt.xticks(fontsize=XY_TICK_FONT_SIZE)
    plt.legend(title="", fontsize=OTHER_FONT_SIZE)

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("figR.pdf")


def main() -> None:
    db: Engine = create_engine(url=f"sqlite:///{DB_PATH}")

    papers: DataFrame = get_papers(db=db)

    df: DataFrame = create_data(df=papers)

    plot(df=df)


if __name__ == "__main__":
    main()
