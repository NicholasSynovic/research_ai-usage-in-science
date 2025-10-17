import json
from pathlib import Path

import click
import pandas
from pandas import DataFrame, Series

from aius.db import DB


def load_author_agreement_data(db: DB) -> DataFrame:
    return pandas.read_sql_table(
        table_name="plos_author_agreement_papers",
        con=db.engine,
    )


def read_json(fp: Path) -> dict:
    with open(file=fp, mode="r") as jfp:
        return json.load(fp=jfp)


def compute_uses_dl(data: dict, aa_df: DataFrame) -> Series:
    accuracy: list[bool] = []

    row: Series
    for _, row in aa_df.iterrows():
        ground_truth: bool = row["uses_dl"]
        computed_value: bool = data[str(row["_id"])]["result"]
        accuracy.append(computed_value == ground_truth)

    return Series(data=accuracy)


def compute_uses_ptms(data: dict, aa_df: DataFrame) -> Series:
    accuracy: list[bool] = []

    row: Series
    for _, row in aa_df.iterrows():
        ground_truth: bool = row["uses_ptms"]
        computed_value: bool = data[str(row["_id"])]["result"]
        accuracy.append(computed_value == ground_truth)

    return Series(data=accuracy)


def compute_identify_ptms(data: dict, aa_df: DataFrame) -> Series:
    # Compute accuracy per model identified, not by if the object matches 1 to 1
    accuracy: list[bool] = []

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
            for gt in ground_truth
        }
        computed_values = {
            cv.replace("deeploc 1.0", "deeploc")
            .replace("-", "")
            .replace("inception resnet", "incresnet")
            for cv in computed_values
        }

        # Get only the unique values
        computed_values: set[str] = set(computed_values)

        print(ground_truth, computed_values, computed_values == ground_truth)

        accuracy.append(computed_values == ground_truth)

    return Series(data=accuracy)


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
def main(
    db_path: Path,
    uses_dl: Path,
    uses_ptms: Path,
    identify_ptms: Path,
) -> None:
    db: DB = DB(db_path=db_path)

    aa_df: DataFrame = load_author_agreement_data(db=db)
    uses_dl_data: dict = read_json(fp=uses_dl)
    uses_ptms_data: dict = read_json(fp=uses_ptms)
    identify_ptms_data: dict = read_json(fp=identify_ptms)

    udl: Series = compute_uses_dl(data=uses_dl_data, aa_df=aa_df)
    uptms: Series = compute_uses_ptms(data=uses_ptms_data, aa_df=aa_df)
    idptms: Series = compute_identify_ptms(data=identify_ptms_data, aa_df=aa_df)

    # print(aa_df["ptm_name_reuse_type"][0])

    print(idptms.sum() / idptms.shape[0])


if __name__ == "__main__":
    main()
