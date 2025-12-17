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
    df.reset_index(drop=True, inplace=True)
    df.rename(columns={"user_prompt": "markdown"}, inplace=True)
    return df


def get_natural_science_papers_per_journal(db: Engine) -> DataFrame:
    sql: str = """
SELECT udl.*, oa.topic_0, oa.topic_1, oa.topic_2 FROM uses_dl_analysis udl
JOIN openalex oa on oa.doi = udl.doi;
"""
    return pd.read_sql(sql=sql, con=db)


def create_data(df: DataFrame) -> Series:
    data: dict[str, list[str]] = {
        "topics": [],
    }

    data["topics"].extend(df["topic_0"].tolist())
    data["topics"].extend(df["topic_1"].tolist())
    data["topics"].extend(df["topic_2"].tolist())

    return (
        DataFrame(data=data)["topics"]
        .value_counts()[FIELD]
        .sort_values(ascending=False)
    )


def main() -> None:
    db: Engine = create_engine(url=f"sqlite:///{DB_PATH}")

    papers: DataFrame = get_natural_science_papers_per_journal(db=db)
    papers = set_dataframe_formatting(df=papers)

    data: Series = create_data(df=papers)

    print(data)
    print(data.sum())


if __name__ == "__main__":
    main()
