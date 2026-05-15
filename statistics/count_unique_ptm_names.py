import json
import sqlite3
import sys
from pathlib import Path

import click
import pandas as pd
from pandas import DataFrame


def load_model_responses(db_path: Path) -> list[dict]:
    query = """
        SELECT model_response
        FROM identify_ptms_analysis
        WHERE model_response IS NOT NULL
          AND TRIM(model_response) != ''
    """

    with sqlite3.connect(db_path) as conn:
        df: DataFrame = pd.read_sql(query, conn)

    return df["model_response"].map(json.loads).tolist()


def model_prose(response: dict) -> str | None:
    try:
        return response["model"].lower()
    except TypeError:
        return None
    except KeyError:
        return None
    except AttributeError:
        return None


def models(response: dict) -> list[str]:
    data: list[str] = []

    for key in response.keys():
        if isinstance(response[key], list):
            for datum in response[key]:
                foo: str | None = model_prose(datum)
                if foo is not None:
                    data.append(foo)
    return data


def to_df(data: list[str]) -> DataFrame:
    return DataFrame(data={"models": data})


@click.command()
@click.option("--db", required=True, type=Path)
def main(db: Path) -> None:
    data: list[str] = []

    responses: list[dict] = load_model_responses(db_path=db)

    response: dict
    for response in responses:
        keys: list[str] = list(response.keys())

        if len(keys) == 0:
            continue

        keys: set[str] = set(keys)

        if keys == {"model", "prose"}:
            datum: str = model_prose(response)
            if datum is None:
                continue
            if isinstance(datum, list):
                continue
            data.append(datum)

        else:
            data.extend(models(response=response))

    df: DataFrame = to_df(data=data)
    df.to_csv(path_or_buf="ptms.csv")


if __name__ == "__main__":
    main()
