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
    df: DataFrame = pandas.read_json(path_or_buf=i).T
    df["result"] = df["result"].astype(dtype=bool)

    print("Total size:", df.shape[0])
    print("Uses PTMs:", df[df["result"] == True].shape[0])
    print("Proportion:", df[df["result"] == True].shape[0] / df.shape[0] * 100)


if __name__ == "__main__":
    main()
