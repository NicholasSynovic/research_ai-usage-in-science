import json
from pathlib import Path

import click
import pandas
from pandas import DataFrame


def parse_json(data: dict[str, list[dict[str, str]]]) -> DataFrame:
    model: dict[str, list[str | None]] = {
        "_id": [],
        "model": [],
        "method": [],
        "classification": [],
    }

    key: str
    val: list[dict]
    for key, val in data.items():
        if len(val) == 0:
            model["_id"].append(key)
            model["model"].append(None)
            model["method"].append(None)
            model["classification"].append(None)
            continue

        if val[0]["model"] == "":
            model["_id"].append(key)
            model["model"].append(None)
            model["method"].append(None)
            model["classification"].append(None)
            continue

        if val[0]["model"] == "None":
            model["_id"].append(key)
            model["model"].append(None)
            model["method"].append(None)
            model["classification"].append(None)
            continue

        obj: dict
        for obj in val:
            model["_id"].append(key)
            model["model"].append(obj["model"])
            model["method"].append(obj["form"])
            model["classification"].append(obj["classification"])

    return DataFrame(data=model)


@click.command()
@click.option(
    "-i",
    required=True,
    type=lambda x: Path(x).resolve(),
)
def main(i: Path) -> None:
    data: dict = json.load(fp=i.open())

    df: DataFrame = parse_json(data=data)
    df.to_json(path_or_buf="identify_reuse.json", indent=4, orient="records")


if __name__ == "__main__":
    main()
