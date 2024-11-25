from pathlib import Path

import click
import pandas
from pandas import DataFrame, Series


def countPapersThatUseDL(df: DataFrame) -> DataFrame:
    counts: Series = df["UsesDL"].value_counts()
    print("Papers That Use DL:", counts["Yes"])
    print("Papers That Do Not Use DL:", counts["No"])

    return df[df["UsesDL"] == "Yes"]


def countReuseMethods(df: DataFrame) -> DataFrame:
    data: dict[str, int] = {
        "Conceptual": 0,
        "Adaptation": 0,
        "Deployment": 0,
    }

    df = df.copy(deep=True)

    df["ReuseMethod"] = df["ReuseMethod"].str.replace(
        pat="Adaption",
        repl="Adaptation",
    )

    data["Conceptual"] = df["ReuseMethod"].str.count(pat="Conceptual").sum()
    data["Adaptation"] = df["ReuseMethod"].str.count(pat="Adaptation").sum()
    data["Deployment"] = df["ReuseMethod"].str.count(pat="Deployment").sum()

    return df


@click.command()
@click.option(
    "-s",
    "--slr",
    "slr",
    help="Path to SLR results",
    required=True,
    type=click.Path(
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
)
def main(slr: Path) -> None:
    df: DataFrame = pandas.read_excel(
        io=slr,
        sheet_name="Form1",
        engine="openpyxl",
    )
    df.columns = df.columns.str.strip()
    df = df.rename(
        columns={
            "Do The Author's Use Deep Learning?": "UsesDL",
            "What Is The Method Of PTM Re-Use Per Model?": "ReuseMethod",
        }
    )

    df["Ignore"] = df["Ignore"].astype(bool)
    keepDF: DataFrame = df[df["Ignore"] == False]  # noqa: E712

    dlDF: DataFrame = countPapersThatUseDL(df=keepDF)

    dlDF = countReuseMethods(df=dlDF)


if __name__ == "__main__":
    main()
