from json import loads
from pathlib import Path

import pandas as pd
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


def set_dataframe_formatting(df: DataFrame) -> DataFrame:
    df["model_response"] = df["model_response"].replace(
        to_replace="",
        value=float("NaN"),
        inplace=False,
    )
    df = df.dropna(inplace=False, ignore_index=True)
    df["model_response"] = df["model_response"].apply(loads)
    df = df[df["model_response"].apply(lambda d: d.get("result") is True)]
    # df = df[df["json_data"].apply(loads)]
    df.reset_index(drop=True, inplace=True)
    df.rename(columns={"user_prompt": "markdown"}, inplace=True)
    return df


def get_natural_science_papers_per_journal(db: Engine) -> DataFrame:
    sql: str = """
SELECT upl.*, oa.json_data FROM uses_ptms_analysis upl
JOIN openalex oa on oa.doi = upl.doi;
"""
    return pd.read_sql(sql=sql, con=db)


def create_data(df: DataFrame) -> Series:
    data: dict[str, list[int]] = {
        "year": [],
    }

    row: Series
    for _, row in df.iterrows():
        json: dict = loads(s=row["json_data"])
        data["year"].append(json["publication_year"])

    return DataFrame(data=data)["year"].value_counts()


def main() -> None:
    db: Engine = create_engine(url=f"sqlite:///{DB_PATH}")

    papers: DataFrame = get_natural_science_papers_per_journal(db=db)
    papers = set_dataframe_formatting(df=papers)

    data: Series = create_data(df=papers)

    print(data)


if __name__ == "__main__":
    main()
