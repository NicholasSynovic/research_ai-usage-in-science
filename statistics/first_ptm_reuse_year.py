import json
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
        SELECT ar.doi, ar.model_response, oa.json_data
        FROM identify_ptm_reuse_analysis ar
        JOIN openalex oa ON oa.doi = ar.doi
        WHERE ar.doi IS NOT NULL
          AND TRIM(ar.doi) != ''
          AND ar.model_response IS NOT NULL
          AND TRIM(ar.model_response) != ''
          AND oa.json_data IS NOT NULL
          AND TRIM(oa.json_data) != ''
    """

    with sqlite3.connect(db_path) as conn:
        return pd.read_sql(query, conn)


def extract_publication_year(json_data: str) -> int | None:
    try:
        data: dict = json.loads(json_data)
    except json.JSONDecodeError:
        return None

    year = data.get("publication_year")
    if isinstance(year, int):
        return year

    return None


def first_reuse_years(rows: DataFrame) -> dict[str, tuple[int, int]]:
    reuse_years: dict[str, dict[int, set[str]]] = {
        "adaptation_reuse": {},
        "conceptual_reuse": {},
        "deployment_reuse": {},
    }

    for _, row in rows.iterrows():
        doi = str(row["doi"]).strip()
        year = extract_publication_year(str(row["json_data"]))
        if year is None:
            continue

        model_response = str(row["model_response"])

        for reuse_type, pattern in REUSE_PATTERNS.items():
            if pattern.search(model_response) is None:
                continue

            reuse_years.setdefault(reuse_type, {})
            reuse_years[reuse_type].setdefault(year, set()).add(doi)

    results: dict[str, tuple[int, int]] = {}
    for reuse_type, years in reuse_years.items():
        if not years:
            continue

        first_year = min(years)
        results[reuse_type] = (first_year, years[first_year])

    return results


@click.command()
@click.option("--db", required=True, type=click.Path(path_type=Path))
def main(db: Path) -> None:
    rows = load_reuse_rows(db_path=db)
    results = first_reuse_years(rows=rows)

    for reuse_type in ("adaptation_reuse", "conceptual_reuse", "deployment_reuse"):
        year_count = results.get(reuse_type)
        if year_count is None:
            print(f"{reuse_type}: no matches")
            continue

        year, doi_count = year_count
        print(f"{reuse_type}: {year} ({doi_count} DOIs)")


if __name__ == "__main__":
    main()
