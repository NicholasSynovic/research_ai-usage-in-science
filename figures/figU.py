import sqlite3
from json import loads
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame, Series


def plot(df: DataFrame) -> None:
    # Aggregate counts per year and classification
    counts = (
        df.groupby(["publication_year", "classification"])
        .size()
        .reset_index(name="count")
    )

    # Pivot for plotting
    pivot = counts.pivot(
        index="publication_year",
        columns="classification",
        values="count",
    ).fillna(0)

    # Plot
    plt.figure()
    pivot.plot(kind="bar")
    plt.xlabel("Year")
    plt.ylabel("Count")
    plt.title("PTM Reuse Impact Counts per Year")
    plt.tight_layout()
    plt.savefig("figU.pdf")


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
    df = df[df["model_response"].str.strip() != ""]

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


def main() -> None:
    db_path: Path = Path("../data/aius_12-17-2025.db").absolute()

    df: DataFrame = load_model_responses(db_path=db_path)

    df = normalize_data(df=df)

    df["classification"] = df["model_response"].map(extract_classification)

    # Optional: drop rows with no classification found
    # df = df[df["classification"].map(bool)]

    df = df.explode(column="classification")

    plot(df)


if __name__ == "__main__":
    main()
