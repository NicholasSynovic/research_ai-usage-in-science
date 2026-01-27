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


def normalize_data(resps: list[dict]) -> list[dict]:
    ALIASES: tuple[str, str, str] = ("model", "result", "response")

    data: list[dict] = []

    resp: dict
    for resp in resps:
        if resp == {}:  # Handles empty dict case
            continue

        for alias in ALIASES:
            if alias in resp:
                resp["model"] = resp[alias]
                break
        data.append(resp)

    return data


def load_model_responses(
    db_path: Path,
    table: str,
    response_column: str,
) -> list[dict[str, Any]]:
    """
    Load model responses from SQLite, excluding empty rows and
    any JSON objects containing the key 'error'.
    """
    query = f"""
        SELECT {response_column}
        FROM {table}
        WHERE {response_column} IS NOT NULL
          AND TRIM({response_column}) != ''
          AND json_type({response_column}, '$.error') IS NULL
    """

    with sqlite3.connect(db_path) as conn:
        df: DataFrame = pd.read_sql(query, conn)

    return df[response_column].apply(loads).tolist()


def main() -> None:
    db_path: Path = Path("../data/aius_12-17-2025.db").absolute()

    model_responses: list[dict] = load_model_responses(
        db_path=db_path,
        table="identify_ptms_analysis",
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
