import sqlite3
from json import loads
from pathlib import Path
from typing import Any

import pandas as pd
from pandas import DataFrame


def parse_resps(resps: list[dict]) -> list[str]:
    data: list[str] = []

    resp: dict
    for resp in resps:
        model: str | Any = resp["model"]

        if isinstance(model, str):
            data.append(model)
            continue

        if isinstance(model, list):
            models: list[str] = parse_resps(model)
            data.extend(models)

    return sorted([d.lower().replace("-", "") for d in data])


def normalize_data(resps: list[str]) -> list[dict]:
    ALIASES: tuple[str, str, str] = ("model", "result", "response")

    data: list[dict] = []

    foo: str
    for foo in resps:
        try:  # Handles empty strings
            resp: dict = loads(foo)
        except:
            continue

        if resp == {}:  # Handles empty dict case
            continue

        if "error" in resp.keys():
            continue

        for alias in ALIASES:
            if alias in resp:
                try:
                    resp["model"] = resp[alias]
                except TypeError:
                    print(resp)
                    input()
                break

        data.append(resp)

    return data


def load_model_responses(
    db_path: Path,
    response_column: str,
) -> list[str]:
    """
    Load model responses from SQLite, excluding empty rows and
    any JSON objects containing the key 'error'.
    """
    query = f"""
        SELECT oa.*, ptm.model_response FROM openalex AS oa
            INNER JOIN natural_science_article_dois ns ON oa.doi = ns.doi
            JOIN identify_ptms_analysis ptm ON  oa.doi = ptm.doi
            WHERE topic_0 IN ('Biochemistry, Genetics and Molecular Biology', 'Agricultural and Biological Sciences', 'Neuroscience')
                OR topic_1 IN ('Biochemistry, Genetics and Molecular Biology', 'Agricultural and Biological Sciences', 'Neuroscience')
                OR topic_2 IN ('Biochemistry, Genetics and Molecular Biology', 'Agricultural and Biological Sciences', 'Neuroscience')
    """

    with sqlite3.connect(db_path) as conn:
        df: DataFrame = pd.read_sql(query, conn)

    return df[response_column].dropna().tolist()


def main() -> None:
    db_path: Path = Path("../data/aius_12-17-2025.db").absolute()

    model_responses: list[str] = load_model_responses(
        db_path=db_path,
        response_column="model_response",
    )

    resps: list[dict] = normalize_data(resps=model_responses)

    models: list[str] = parse_resps(resps=resps)

    print("Total number of models:", len(models))

    df: DataFrame = DataFrame(data={"models": models})
    print("Total number of unique models:", df["models"].unique().shape[0])
    print(df["models"].value_counts())
    df.to_csv("models.csv", sep=",", index=False)

    # model: str
    # try:
    #     model = resp["model"]
    # except KeyError:
    #     try:
    #         model = resp["response"]
    #     except KeyError:
    #         print(resp)
    #         input()

    # print(model)


if __name__ == "__main__":
    main()
