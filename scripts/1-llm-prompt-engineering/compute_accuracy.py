import json
from pathlib import Path

import click
import pandas
from pandas import DataFrame, Series

from aius.db.db import DB


def load_author_agreement_data(db: DB) -> DataFrame:
    return pandas.read_sql_table(
        table_name="plos_author_agreement_papers",
        con=db.engine,
    )


def read_json(fp: Path) -> dict:
    with open(file=fp, mode="r") as jfp:
        return json.load(fp=jfp)


def compute_uses_dl(data: dict, aa_df: DataFrame) -> DataFrame:
    df_data: dict[str, list[bool]] = {
        "value": [],
        "accuracy": [],
    }

    row: Series
    for _, row in aa_df.iterrows():
        ground_truth: bool = row["uses_dl"]
        computed_value: bool = data[str(row["_id"])]["result"]

        # Get only the unique values
        df_data["value"].append(computed_value)
        df_data["accuracy"].append(computed_value == ground_truth)

    return DataFrame(data=df_data)


def compute_uses_ptms(data: dict, aa_df: DataFrame) -> DataFrame:
    df_data: dict[str, list[bool]] = {
        "value": [],
        "accuracy": [],
    }

    row: Series
    for _, row in aa_df.iterrows():
        ground_truth: bool = row["uses_ptms"]
        computed_value: bool = data[str(row["_id"])]["result"]

        # Get only the unique values
        df_data["value"].append(computed_value)
        df_data["accuracy"].append(computed_value == ground_truth)

    return DataFrame(data=df_data)


def compute_identify_ptms(data: dict, aa_df: DataFrame) -> DataFrame:
    df_data: dict[str, list[set | bool]] = {
        "value": [],
        "accuracy": [],
    }

    row: Series
    for _, row in aa_df.iterrows():
        ground_truth: set[str] = set(json.loads(s=row["ptm_name_reuse_type"])["ptm"])
        computed_value_list: list[dict | None] = data[str(row["_id"])]

        computed_values: list[str] = []
        if len(computed_value_list) > 0:
            computed_values = [x["model"].lower() for x in computed_value_list]

            try:
                computed_values.remove("")
            except ValueError:
                pass

            try:
                computed_values.remove("none")
            except ValueError:
                pass

        # Format content in both sets to account for formatting differences
        ground_truth = {
            gt.replace("deeploc 1.0", "deeploc")
            .replace("-", "")
            .replace("inception resnet", "incresnet")
            .replace("inceptionresnetv2", "incresnetv2")
            for gt in ground_truth
        }
        computed_values_set: set[str] = set(
            [
                cv.replace("deeploc 1.0", "deeploc")
                .replace("-", "")
                .replace("inception resnet", "incresnet")
                .replace("inceptionresnetv2", "incresnetv2")
                for cv in computed_values
            ]
        )

        # Get only the unique values
        df_data["value"].append(computed_values_set)
        df_data["accuracy"].append(computed_values_set == ground_truth)

    return DataFrame(data=df_data)


def compute_identify_reuse(data: dict, aa_df: DataFrame) -> DataFrame:
    df_data: dict[str, list[list[str] | bool]] = {
        "value": [],
        "accuracy": [],
    }

    row: Series
    for _, row in aa_df.iterrows():
        ground_truth: list[str] = sorted(
            json.loads(s=row["ptm_name_reuse_type"])["reuse"]
        )

        computed_value_list: list[dict | None] = data[str(row["_id"])]

        computed_values: list[str] = []
        if len(computed_value_list) > 0:
            computed_values = sorted(
                [
                    x["classification"].lower().strip("_reuse")
                    for x in computed_value_list
                ]
            )

            try:
                computed_values.remove("")
            except ValueError:
                pass

            try:
                computed_values.remove("none")
            except ValueError:
                pass

            try:
                computed_values.remove("non")
            except ValueError:
                pass

        # Get only the unique values
        df_data["value"].append(computed_values)
        df_data["accuracy"].append(computed_values == ground_truth)

    return DataFrame(data=df_data)


@click.command()
@click.option(
    "--db-path",
    required=True,
    help="Path to database",
    type=lambda x: Path(x).resolve(),
)
@click.option(
    "--uses-dl",
    required=True,
    help="Path to uses_dl JSON file",
    type=lambda x: Path(x).resolve(),
)
@click.option(
    "--uses-ptms",
    required=True,
    type=lambda x: Path(x).resolve(),
    help="Path to uses_ptms JSON file",
)
@click.option(
    "--identify-ptms",
    required=True,
    type=lambda x: Path(x).resolve(),
    help="Path to identify_ptms JSON file",
)
@click.option(
    "--identify-reuse",
    required=True,
    type=lambda x: Path(x).resolve(),
    help="Path to identify_reuse JSON file",
)
def main(
    db_path: Path,
    uses_dl: Path,
    uses_ptms: Path,
    identify_ptms: Path,
    identify_reuse: Path,
) -> None:
    # Connect to the database
    db: DB = DB(db_path=db_path)

    # Load data from the database
    aa_df: DataFrame = load_author_agreement_data(db=db)

    # Read in JSON files
    uses_dl_data: dict = read_json(fp=uses_dl)
    uses_ptms_data: dict = read_json(fp=uses_ptms)
    identify_ptms_data: dict = read_json(fp=identify_ptms)
    identify_reuse_data: dict = read_json(fp=identify_reuse)

    # Compute uses_dl accuracy
    uses_dl_df: DataFrame = compute_uses_dl(data=uses_dl_data, aa_df=aa_df)
    print(
        "0. Accuracy:",
        uses_dl_df["accuracy"].sum() / uses_dl_df.shape[0] * 100,
        "Truthy:",
        uses_dl_df[uses_dl_df["value"] == True].shape[0],
    )

    # Computes uses_ptms accuracy
    uses_ptms_df: DataFrame = compute_uses_ptms(data=uses_ptms_data, aa_df=aa_df)
    print(
        "1. Accuracy:",
        uses_ptms_df["accuracy"].sum() / uses_ptms_df.shape[0] * 100,
        "Truthy:",
        uses_ptms_df[uses_ptms_df["value"] == True].shape[0],
    )

    # Computes identify_ptms accuracy
    identify_ptms_df: DataFrame = compute_identify_ptms(
        data=identify_ptms_data, aa_df=aa_df
    )
    print(
        "2. Accuracy:",
        identify_ptms_df["accuracy"].sum() / identify_ptms_df.shape[0] * 100,
        "Truthy:",
        identify_ptms_df[identify_ptms_df["value"] != set()].shape[0],
    )

    # Computes identify_reuse accuracy
    identify_reuse_df: DataFrame = compute_identify_reuse(
        data=identify_reuse_data, aa_df=aa_df
    )
    print(
        "3. Accuracy:",
        identify_reuse_df["accuracy"].sum() / identify_reuse_df.shape[0] * 100,
        "Truthy:",
        identify_reuse_df[identify_reuse_df["value"].str.len() != 0].shape[0],
    )


if __name__ == "__main__":
    main()
