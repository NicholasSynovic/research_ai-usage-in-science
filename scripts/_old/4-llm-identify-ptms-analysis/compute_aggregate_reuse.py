import json
from pathlib import Path

import click
import pandas
from pandas import DataFrame


@click.command()
@click.option(
    "-i",
    required=True,
    type=lambda x: Path(x).resolve(),
)
def main(i: Path) -> None:
    data: dict = json.load(fp=i.open(mode="r"))

    conceptual: int = 0
    adaptation: int = 0
    deployment: int = 0

    val: list[dict]

    for _, val in data.items():
        if len(val) == 0:
            continue

        if val[0]["model"] == "":
            continue

        if val[0]["model"] == "None":
            continue

        obj: dict
        for obj in val:
            match obj["classification"]:
                case "conceptual_reuse":
                    conceptual += 1
                case "adaptation_reuse":
                    adaptation += 1
                case "deployment_reuse":
                    deployment += 1
                case _:
                    print(obj)

    print("Conceptual:", conceptual)
    print("Adaptation:", adaptation)
    print("Deployment:", deployment)


if __name__ == "__main__":
    main()
