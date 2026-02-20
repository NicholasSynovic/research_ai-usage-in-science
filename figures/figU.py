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

    fig, ax = plt.subplots(figsize=(12, 9))
    sns.barplot(
        data=counts,
        x="publication_year",
        y="count",
        hue="classification",
        hue_order=[
            "Observation",
            "Hypothesis",
            "Background",
            "Analysis",
            "Test",
        ],
        ax=ax,
    )

    if log_scale:
        ax.set_yscale("log")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_xlabel("Year", fontsize=XY_LABEL_FONT_SIZE)
    ax.set_ylabel("Count", fontsize=XY_LABEL_FONT_SIZE)
    ax.set_title(
        "PTM Reuse Impact Counts per Year",
        fontsize=TITLE_FONT_SIZE,
    )
    ax.tick_params(axis="both", labelsize=XY_TICK_FONT_SIZE)
    ax.tick_params(axis="x", rotation=45)
    ax.legend(
        title="Scientific Process",
        fontsize=OTHER_FONT_SIZE,
        title_fontsize=OTHER_FONT_SIZE,
        frameon=True,
    )

    for container in ax.containers:
        if isinstance(container, BarContainer):
            ax.bar_label(
                container,
                fmt="{:,.0f}",
                padding=3,
                fontsize=OTHER_FONT_SIZE,
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
        return [obj["step"]] if "step" in obj else []

    if isinstance(obj, list):
        return [
            item["step"] for item in obj if isinstance(item, dict) and "step" in item
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
	impact.model_response
FROM
	openalex oa
INNER JOIN natural_science_article_dois ns ON oa.doi = ns.doi
JOIN identify_ptm_impact_analysis impact ON oa.doi = impact.doi;
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
    default=Path("figU.pdf").absolute(),
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
def main(db_path: Path, output_path: Path, log_scale: bool = False) -> None:
    db_path = db_path.absolute()
    output_path = output_path.absolute()

    df: DataFrame = load_model_responses(db_path=db_path)

    df = normalize_data(df=df)

    df["classification"] = df["model_response"].map(extract_classification)

    # Optional: drop rows with no classification found
    # df = df[df["classification"].map(bool)]

    df = df.explode(column="classification")

    plot(df, output_path=output_path, log_scale=log_scale)


if __name__ == "__main__":
    main()
