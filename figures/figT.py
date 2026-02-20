import sqlite3
from json import loads
from pathlib import Path
from typing import Any

import click
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.container import BarContainer
from matplotlib.ticker import FuncFormatter
from pandas import DataFrame

SUPTITLE_FONT_SIZE: int = 24
TITLE_FONT_SIZE: int = 22
XY_LABEL_FONT_SIZE: int = 20
XY_TICK_FONT_SIZE: int = 18
OTHER_FONT_SIZE: int = XY_TICK_FONT_SIZE


def plot(df: DataFrame, output_path: Path, log_scale: bool = False) -> None:
    # Aggregate counts per year and classification
    counts = df.groupby(["publication_year", "classification"]).size().reset_index()
    counts.columns = ["publication_year", "classification", "count"]

    counts["classification"] = counts["classification"].replace(
        to_replace="adaptation_reuse", value="Adaptation Reuse"
    )
    counts["classification"] = counts["classification"].replace(
        to_replace="conceptual_reuse", value="Conceptual Reuse"
    )
    counts["classification"] = counts["classification"].replace(
        to_replace="deployment_reuse", value="Deployment Reuse"
    )

    ymax: int = counts[counts["classification"] == "Adaptation Reuse"]["count"].max()

    classifications = [
        "Adaptation Reuse",
        "Deployment Reuse",
        "Conceptual Reuse",
    ]
    panel_labels = ["(A)", "(B)", "(C)"]

    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(24, 8), sharey=True)
    for index, classification in enumerate(classifications):
        ax = axes[index]
        panel_data = counts.loc[counts["classification"] == classification]

        sns.barplot(
            data=panel_data,
            x="publication_year",
            y="count",
            ax=ax,
        )

        if log_scale:
            ax.set_yscale("log")
        else:
            ax.set_ylim(0, ymax * 1.3)

        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}"))
        ax.set_xlabel("Year", fontsize=XY_LABEL_FONT_SIZE)
        ax.set_ylabel("Count", fontsize=XY_LABEL_FONT_SIZE)
        ax.set_title(classification, fontsize=TITLE_FONT_SIZE)
        ax.tick_params(axis="both", labelsize=XY_TICK_FONT_SIZE)
        ax.tick_params(axis="x", rotation=45)

        if ax.get_legend() is not None:
            ax.get_legend().remove()

        for container in ax.containers:
            if isinstance(container, BarContainer):
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
        "PTM Reuse Pattern Counts per Year",
        fontsize=SUPTITLE_FONT_SIZE,
    )
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def extract_classification(obj: Any) -> list[Any]:
    """
    Extract classification values from:
      - a dict
      - a list of dicts

    Always returns a list (possibly empty).
    """
    if isinstance(obj, dict):
        return [obj["classification"]] if "classification" in obj else []

    if isinstance(obj, list):
        return [
            item["classification"]
            for item in obj
            if isinstance(item, dict) and "classification" in item
        ]

    return []


def normalize_data(df: DataFrame) -> DataFrame:
    # 1. Drop NULL and empty / whitespace-only strings
    df = df.dropna(subset=["model_response"])
    df = df.loc[df["model_response"].str.strip() != ""]

    # 2. Parse JSON safely
    def parse_json(s: str) -> dict[str, Any] | None:
        try:
            obj = loads(s)
            return obj if isinstance(obj, dict) and obj else None
        except Exception:
            return None

    df["model_response"] = df["model_response"].map(parse_json)

    # 3. Drop malformed JSON or empty dicts
    df = df.dropna(subset=["model_response"])

    return df


def load_model_responses(db_path: Path) -> DataFrame:
    query = f"""
        SELECT
  oa.doi,
  json_extract(
    oa.json_data, '$.publication_year'
  ) AS publication_year,
  reuse.model_response
FROM
  openalex oa
  INNER JOIN natural_science_article_dois ns ON oa.doi = ns.doi
  JOIN identify_ptm_reuse_analysis reuse ON oa.doi = reuse.doi;
    """

    with sqlite3.connect(db_path) as conn:
        df: DataFrame = pd.read_sql(query, conn)

    return df.sort_values(by="publication_year")


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
    default=Path("figT.pdf").absolute(),
    type=click.Path(path_type=Path),
    show_default=True,
    help="Output path for the plot.",
)
@click.option(
    "--log-scale",
    "log_scale",
    default=False,
    type=bool,
    show_default=True,
    help="Use log-scaling on the Y-axis.",
)
def main(db_path: Path, output_path: Path, log_scale: bool) -> None:
    db_path = db_path.absolute()
    output_path = output_path.absolute()

    df: DataFrame = load_model_responses(db_path=db_path)

    df = normalize_data(df=df)

    df["classification"] = df["model_response"].map(extract_classification)

    df = df.explode(column="classification")

    plot(df, output_path=output_path, log_scale=log_scale)


if __name__ == "__main__":
    main()
