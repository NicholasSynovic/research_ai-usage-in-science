import re
import sqlite3
from pathlib import Path

import click
import pandas as pd
from pandas import DataFrame

FIELD: list[str] = [
    "Biochemistry, Genetics and Molecular Biology",
    "Neuroscience",
    "Environmental Science",
    "Agricultural and Biological Sciences",
    "Chemistry",
    "Earth and Planetary Sciences",
    "Immunology and Microbiology",
    "Physics and Astronomy",
]

REUSE_PATTERNS: dict[str, re.Pattern[str]] = {
    "adaptation_reuse": re.compile(r'"adaptation_reuse"'),
    "conceptual_reuse": re.compile(r'"conceptual_reuse"'),
    "deployment_reuse": re.compile(r'"deployment_reuse"'),
}


def load_reuse_rows(db_path: Path) -> DataFrame:
    query = """
        SELECT
            oa.doi,
            oa.topic_0,
            oa.topic_1,
            oa.topic_2,
            reuse.model_response
        FROM
            openalex oa
        JOIN
            natural_science_article_dois ns
        ON
            oa.doi = ns.doi
        JOIN
            identify_ptm_reuse_analysis reuse
        ON
            oa.doi = reuse.doi
        WHERE
            oa.doi IS NOT NULL
            AND TRIM(oa.doi) != ''
            AND reuse.model_response IS NOT NULL
            AND TRIM(reuse.model_response) != ''
    """

    with sqlite3.connect(db_path) as conn:
        return pd.read_sql(query, conn)


def count_fields_by_reuse(rows: DataFrame) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, set[str]]] = {
        "adaptation_reuse": {field: set() for field in FIELD},
        "conceptual_reuse": {field: set() for field in FIELD},
        "deployment_reuse": {field: set() for field in FIELD},
    }

    for _, row in rows.iterrows():
        doi = str(row["doi"]).strip()
        topics = [str(row["topic_0"]), str(row["topic_1"]), str(row["topic_2"])]
        model_response = str(row["model_response"])

        matched_fields = {topic for topic in topics if topic in FIELD}
        if not matched_fields:
            continue

        for reuse_type, pattern in REUSE_PATTERNS.items():
            if pattern.search(model_response) is None:
                continue

            for field in matched_fields:
                counts[reuse_type][field].add(doi)

    return {
        reuse_type: {field: len(dois) for field, dois in field_counts.items()}
        for reuse_type, field_counts in counts.items()
    }


def top_fields_with_ties(
    field_counts: dict[str, int], limit: int = 3
) -> list[tuple[str, int]]:
    ranked = sorted(field_counts.items(), key=lambda item: item[1], reverse=True)
    if not ranked:
        return []

    cutoff_index = min(limit, len(ranked)) - 1
    cutoff_count = ranked[cutoff_index][1]
    return [item for item in ranked if item[1] >= cutoff_count]


@click.command()
@click.option("--db", required=True, type=click.Path(path_type=Path))
def main(db: Path) -> None:
    rows = load_reuse_rows(db_path=db)
    counts = count_fields_by_reuse(rows=rows)

    labels = {
        "adaptation_reuse": "Adaptation Reuse",
        "conceptual_reuse": "Conceptual Reuse",
        "deployment_reuse": "Deployment Reuse",
    }

    for reuse_type in ("adaptation_reuse", "conceptual_reuse", "deployment_reuse"):
        print(labels[reuse_type])
        for field, count in top_fields_with_ties(counts[reuse_type]):
            print(f"{field}: {count}")
        print()


if __name__ == "__main__":
    main()
