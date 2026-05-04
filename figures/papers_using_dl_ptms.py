from json import loads
from pathlib import Path
from typing import Any

import click
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.ticker import FuncFormatter
from pandas import DataFrame
from sqlalchemy import Engine, create_engine

SUPTITLE_FONT_SIZE: int = 24
XY_LABEL_FONT_SIZE: int = 20
XY_TICK_FONT_SIZE: int = 18
OTHER_FONT_SIZE: int = XY_TICK_FONT_SIZE
START_YEAR: int = 2016
END_YEAR: int = 2025

DL_LABEL: str = "DL Usage"
PTM_LABEL: str = "PTM Usage"


def load_dl_rows(db: Engine) -> DataFrame:
    sql: str = """
SELECT
    udl.doi,
    CAST(json_extract(oa.json_data, '$.publication_year') AS INTEGER) AS publication_year,
    udl.model_response
FROM
    uses_dl_analysis udl
JOIN
    openalex oa
ON
    oa.doi = udl.doi
INNER JOIN
    natural_science_article_dois ns
ON
    ns.doi = udl.doi;
"""
    return pd.read_sql(sql=sql, con=db)


def load_ptm_reuse_rows(db: Engine) -> DataFrame:
    sql: str = """
SELECT
    reuse.doi,
    CAST(json_extract(oa.json_data, '$.publication_year') AS INTEGER) AS publication_year,
    reuse.model_response
FROM
    identify_ptm_reuse_analysis reuse
JOIN
    openalex oa
ON
    oa.doi = reuse.doi
INNER JOIN
    natural_science_article_dois ns
ON
    ns.doi = reuse.doi;
"""
    return pd.read_sql(sql=sql, con=db)


def parse_json(value: str) -> dict[str, Any] | list[Any] | None:
    if not isinstance(value, str) or value.strip() == "":
        return None

    try:
        parsed: Any = loads(value)
    except Exception:
        return None

    if isinstance(parsed, dict | list):
        return parsed

    return None


def has_classification(obj: Any) -> bool:
    if isinstance(obj, dict):
        if "classification" in obj and obj["classification"] not in (None, ""):
            return True
        return any(has_classification(value) for value in obj.values())

    if isinstance(obj, list):
        return any(has_classification(item) for item in obj)

    return False


def create_dl_counts(df: DataFrame) -> DataFrame:
    parsed: DataFrame = df.copy()
    parsed["parsed_model_response"] = parsed["model_response"].map(parse_json)

    def is_dl_paper(obj: Any) -> bool:
        return isinstance(obj, dict) and obj.get("result") is True

    filtered: DataFrame = parsed[parsed["parsed_model_response"].map(is_dl_paper)]
    filtered = filtered.dropna(subset=["publication_year"])
    filtered = filtered.drop_duplicates(subset=["doi"], keep="first")

    counts: DataFrame = (
        filtered.groupby("publication_year")
        .size()
        .reset_index(name="count")
        .sort_values(by="publication_year")
    )

    counts["publication_year"] = counts["publication_year"].astype(int)

    return counts


def create_ptm_reuse_counts(df: DataFrame) -> DataFrame:
    parsed: DataFrame = df.copy()
    parsed["parsed_model_response"] = parsed["model_response"].map(parse_json)

    filtered: DataFrame = parsed[
        parsed["parsed_model_response"].map(has_classification)
    ]
    filtered = filtered.dropna(subset=["publication_year"])
    filtered = filtered.drop_duplicates(subset=["doi"], keep="first")

    counts: DataFrame = (
        filtered.groupby("publication_year")
        .size()
        .reset_index(name="count")
        .sort_values(by="publication_year")
    )

    counts["publication_year"] = counts["publication_year"].astype(int)

    return counts


def create_complete_year_counts(counts: DataFrame, label: str) -> DataFrame:
    years: list[int] = list(range(START_YEAR, END_YEAR + 1))
    base: DataFrame = DataFrame(data={"publication_year": years})

    merged: DataFrame = base.merge(
        counts,
        on="publication_year",
        how="left",
    )
    merged["count"] = merged["count"].fillna(value=0).astype(int)
    merged["category"] = label

    return merged


def plot_counts(df: DataFrame, output_path: Path) -> None:
    sns.set_theme(style="ticks")
    fig, ax = plt.subplots(figsize=(8, 8))
    sns.barplot(
        data=df,
        x="publication_year",
        y="count",
        hue="category",
        hue_order=[DL_LABEL, PTM_LABEL],
        palette={DL_LABEL: "#4C78A8", PTM_LABEL: "#F58518"},
        ax=ax,
    )

    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_xlabel("Year", fontsize=XY_LABEL_FONT_SIZE)
    ax.set_ylabel("Count", fontsize=XY_LABEL_FONT_SIZE)
    # ax.set_title(
    #     "Papers Using Deep Learning and Reusing PTMs per Year",
    #     fontsize=SUPTITLE_FONT_SIZE,
    # )
    xtick_labels: list[str] = []
    for year in range(START_YEAR, END_YEAR + 1):
        if year % 2 == 0:
            xtick_labels.append(str(year))
        else:
            xtick_labels.append("")
    ax.set_xticklabels(xtick_labels)

    ax.tick_params(axis="both", labelsize=XY_TICK_FONT_SIZE)
    ax.tick_params(axis="x")
    ax.legend(title="", fontsize=OTHER_FONT_SIZE)
    ax.grid(False)

    for container in ax.containers:
        ax.bar_label(
            container,
            fmt="{:,.0f}",
            padding=3,
            fontsize=OTHER_FONT_SIZE,
        )

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
    default=Path("papers_using_dl_ptms.pdf").absolute(),
    type=click.Path(path_type=Path),
    show_default=True,
    help="Output path for combined paper counts plot.",
)
def main(db_path: Path, output_path: Path) -> None:
    db_path = db_path.absolute()
    output_path = output_path.absolute()

    db: Engine = create_engine(url=f"sqlite:///{db_path}")

    dl_df: DataFrame = load_dl_rows(db=db)
    ptm_df: DataFrame = load_ptm_reuse_rows(db=db)

    dl_counts: DataFrame = create_dl_counts(df=dl_df)
    ptm_counts: DataFrame = create_ptm_reuse_counts(df=ptm_df)

    dl_complete: DataFrame = create_complete_year_counts(
        counts=dl_counts,
        label=DL_LABEL,
    )
    ptm_complete: DataFrame = create_complete_year_counts(
        counts=ptm_counts,
        label=PTM_LABEL,
    )
    combined: DataFrame = pd.concat([dl_complete, ptm_complete], ignore_index=True)

    plot_counts(df=combined, output_path=output_path)

    print(combined["count"].sum())


if __name__ == "__main__":
    main()
