"""
Compute author agreement
"""

import json
from pathlib import Path

import click
import pandas
from pandas import DataFrame


def read_json(json_fp: Path) -> dict:
    with open(file=json_fp, mode="r") as jfp:
        return json.load(fp=jfp)


def handle_uses_dl(json_data: dict, author_agreement_data: dict) -> dict:
    data: dict[str, list[int | bool]] = {
        "_id": [],
        "plos_paper_id": [],
        "correct": [],
    }

    uses_dl_data: dict = author_agreement_data["uses_dl"]

    key: int
    for key in uses_dl_data.keys():
        ground_truth: int = uses_dl_data[key]

        computed_object: dict = json_data[key]

        computed_value: int = 0
        if (computed_object["result"] == True) and computed_object["prose"] != "":
            computed_value = 1

        data["_id"].append(key)
        data["plos_paper_id"].append(author_agreement_data["plos_paper_id"][key])
        data["correct"].append(ground_truth == computed_value)

    return data


@click.command()
@click.option(
    "--json-fp",
    required=True,
    help="Path to JSON file",
    type=lambda x: Path(x).resolve(),
)
@click.option(
    "--aa-fp",
    required=True,
    help="Path to Author Agreement JSONfile",
    type=lambda x: Path(x).resolve(),
)
@click.option(
    "-q",
    required=True,
    type=click.Choice(choices=[1, 2, 3, 4]),
    help="Author agreement question to check",
)
def main(json_fp: Path, aa_fp: Path, q: int) -> None:
    json_data: dict = read_json(json_fp=json_fp)
    author_agreement_data: dict = read_json(json_fp=aa_fp)

    agreement: dict = handle_uses_dl(
        json_data=json_data,
        author_agreement_data=author_agreement_data,
    )

    print(DataFrame(data=agreement))

    # agreement["accuracy"] = sum(agreement["correct"]) / len(agreement["correct"])


if __name__ == "__main__":
    main()
