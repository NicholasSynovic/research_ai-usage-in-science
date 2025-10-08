import pickle
from pathlib import Path

import click
from pandas import DataFrame, Series
from requests import Response


def read_pickle(fp: Path) -> DataFrame:
    # Load pickle file as DataFrame
    df: DataFrame = pickle.load(file=fp.open(mode="rb"))

    return df.sort_values(by="filename", ignore_index=True)


def parse_responses(df: DataFrame) -> None:
    row: Series
    for _, row in df.iterrows():
        filename: str = row["filename"]
        resp: Response = row["response_obj"]

        print(filename)
        print(resp.json()["response"])


@click.command()
@click.option(
    "-i",
    "--input-path",
    help="Path to Python Pickle file",
    type=lambda x: Path(x).resolve(),
)
def main(input_path: Path) -> None:
    # Load pickle file as DataFrame
    df: DataFrame = read_pickle(fp=input_path)

    parse_responses(df=df)


if __name__ == "__main__":
    main()
