import warnings
from json import loads
from pathlib import Path

import pandas as pd
from pandas import DataFrame, Series
from sqlalchemy import Engine, create_engine

warnings.filterwarnings("ignore")

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
    df.reset_index(drop=True, inplace=True)
    df.rename(columns={"user_prompt": "markdown"}, inplace=True)
    return df


def get_natural_science_papers_per_journal(db: Engine) -> DataFrame:
    sql: str = "SELECT * FROM identify_ptm_reuse_analysis;"
    return pd.read_sql(sql=sql, con=db)


def create_data(df: DataFrame) -> Series:
    data: dict[str, list[str]] = {
        "reuse": [],
    }

    for _, row in df.iterrows():
        json: dict = row["model_response"]

        try:
            data["reuse"].append(json["classification"])
            continue
        except KeyError:
            pass

        try:
            for datum in json["response"]:
                data["reuse"].append(datum["classification"])
            continue
        except KeyError:
            pass

        try:
            for datum in json["model"]:
                data["reuse"].append(datum["classification"])
            continue
        except KeyError:
            pass

        try:
            for datum in json["models"]:
                data["reuse"].append(datum["classification"])
            continue
        except KeyError:
            pass

        try:
            for datum in json["result"]:
                data["reuse"].append(datum["classification"])
            continue
        except KeyError:
            pass

    return DataFrame(data=data)["reuse"].value_counts()


def main() -> None:
    db: Engine = create_engine(url=f"sqlite:///{DB_PATH}")

    papers: DataFrame = get_natural_science_papers_per_journal(db=db)
    papers = set_dataframe_formatting(df=papers)

    data: Series = create_data(df=papers)

    print(data)
    quit()
    print(data.sum())


if __name__ == "__main__":
    main()
