import re
import sqlite3
from pathlib import Path

import click
import pandas as pd
from pandas import DataFrame

REUSE_PATTERNS: dict[str, re.Pattern[str]] = {
    "adaptation_reuse": re.compile(r'"adaptation_reuse"'),
    "conceptual_reuse": re.compile(r'"conceptual_reuse"'),
    "deployment_reuse": re.compile(r'"deployment_reuse"'),
}


def load_reuse_rows(db_path: Path) -> DataFrame:
    query = """
        SELECT doi, model_response
        FROM identify_ptm_reuse_analysis
        WHERE doi IS NOT NULL
          AND TRIM(doi) != ''
          AND model_response IS NOT NULL
          AND TRIM(model_response) != ''
    """

    with sqlite3.connect(db_path) as conn:
        return pd.read_sql(query, conn)


def count_distinct_dois_by_reuse(rows: DataFrame) -> dict[str, int]:
    doi_sets: dict[str, set[str]] = {
        "adaptation_reuse": set(),
        "conceptual_reuse": set(),
        "deployment_reuse": set(),
    }

    for _, row in rows.iterrows():
        doi = str(row["doi"]).strip()
        model_response = str(row["model_response"])

        # print(re.search('"classification"', model_response))

        for reuse_type, pattern in REUSE_PATTERNS.items():
            if pattern.search(model_response) is not None:
                doi_sets[reuse_type].add(doi)

    return {reuse_type: len(dois) for reuse_type, dois in doi_sets.items()}


@click.command()
@click.option("--db", required=True, type=click.Path(path_type=Path))
def main(db: Path) -> None:
    rows = load_reuse_rows(db_path=db)

    counts = count_distinct_dois_by_reuse(rows=rows)

    print(f"adaptation_reuse: {counts['adaptation_reuse']}")
    print(f"conceptual_reuse: {counts['conceptual_reuse']}")
    print(f"deployment_reuse: {counts['deployment_reuse']}")


if __name__ == "__main__":
    main()
