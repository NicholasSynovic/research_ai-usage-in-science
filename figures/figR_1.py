from json import loads
from pathlib import Path
from typing import Any

import click
import pandas as pd
from pandas import DataFrame
from sqlalchemy import Engine, create_engine

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


def load_papers(db: Engine) -> DataFrame:
    sql: str = """
SELECT
    udl.doi,
    udl.model_response,
    oa.topic_0,
    oa.topic_1,
    oa.topic_2,
    CAST(json_extract(oa.json_data, '$.publication_year') AS INTEGER) AS publication_year
FROM
    uses_dl_analysis udl
JOIN
    openalex oa
ON
    oa.doi = udl.doi;
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


def create_field_dataframes(df: DataFrame) -> dict[str, DataFrame]:
    data: dict[str, list[str | int]] = {
        "year": [],
        "field": [],
        "dl_using": [],
        "no_dl": [],
    }

    for _, row in df.iterrows():
        parsed_response = parse_json(str(row["model_response"]))
        if not isinstance(parsed_response, dict):
            continue

        result = parsed_response.get("result")
        if result is True:
            dl_using = 1
            no_dl = 0
        elif result is False:
            dl_using = 0
            no_dl = 1
        else:
            continue

        topics: list[str] = [
            str(row["topic_0"]),
            str(row["topic_1"]),
            str(row["topic_2"]),
        ]

        for topic in topics:
            if topic in FIELD:
                data["year"].append(int(row["publication_year"]))
                data["field"].append(topic)
                data["dl_using"].append(dl_using)
                data["no_dl"].append(no_dl)

    data_df = DataFrame(data=data)
    if data_df.empty:
        return {
            field: DataFrame(columns=["year", "dl_using", "no_dl"]) for field in FIELD
        }

    min_year = int(data_df["year"].min())
    max_year = int(data_df["year"].max())
    years = list(range(min_year, max_year + 1))

    field_dataframes: dict[str, DataFrame] = {}
    for field in FIELD:
        field_df = data_df.loc[data_df["field"] == field]
        field_counts = (
            field_df.groupby("year", as_index=False)[["dl_using", "no_dl"]].sum()
            if not field_df.empty
            else DataFrame(columns=["year", "dl_using", "no_dl"])
        )

        field_counts = (
            field_counts.set_index("year")
            .reindex(years, fill_value=0)
            .reset_index()
            .rename(columns={"index": "year"})
        )
        field_counts[["dl_using", "no_dl"]] = field_counts[
            ["dl_using", "no_dl"]
        ].astype(int)
        field_dataframes[field] = field_counts

    return field_dataframes


@click.command()
@click.option(
    "--db",
    "db_path",
    default=Path("../data/aius_12-17-2025.db").absolute(),
    type=click.Path(path_type=Path),
    show_default=True,
    help="Path to the SQLite database.",
)
def main(db_path: Path) -> None:
    db_path = db_path.absolute()
    db: Engine = create_engine(url=f"sqlite:///{db_path}")

    papers: DataFrame = load_papers(db=db)
    field_dataframes = create_field_dataframes(df=papers)

    for field, field_df in field_dataframes.items():
        print(field)
        print(field_df.to_string(index=False))
        print()


if __name__ == "__main__":
    main()
