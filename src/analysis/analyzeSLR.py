from pathlib import Path

import click
import pandas
from pandas import DataFrame, Series

from src.analysis import DOIS


def readDF(fp: Path) -> DataFrame:
    print("Number Of Samples:", len(set(DOIS)))

    df: DataFrame = pandas.read_excel(
        io=fp,
        sheet_name="Form1",
        engine="openpyxl",
    )

    print("Rows Recorded:", df.shape[0])

    df.columns = df.columns.str.strip()
    df = df.rename(
        columns={
            "Do The Author's Use Deep Learning?": "UsesDL",
            "What Is The Method Of PTM Re-Use Per Model?": "ReuseMethod",
            "Paper DOI": "DOI",
        }
    )
    df["ReuseMethod"] = df["ReuseMethod"].str.replace(
        pat="Adaption",
        repl="Adaptation",
    )

    df = df[df["DOI"].isin(values=DOIS)]
    print("DOIs Recorded:", df.shape[0])

    df["Ignore"] = df["Ignore"].astype(bool)
    df = df[df["Ignore"] == False]  # noqa: E712
    print("Unqiue DOIs Read And Recorded:", df.shape[0])

    print("Missing DOIs:", DOIS.difference(df["DOI"]))

    return df


def countPapersThatUseDL(df: DataFrame) -> DataFrame:
    counts: Series = df["UsesDL"].value_counts()
    print("Papers That Use DL:", counts["Yes"])
    print("Papers That Do Not Use DL:", counts["No"])

    return df[df["UsesDL"] == "Yes"]


def countReuseMethodsPerPaper(df: DataFrame) -> None:
    data: dict[str, int] = {
        "Conceptual": 0,
        "Adaptation": 0,
        "Deployment": 0,
    }

    data["Conceptual"] = (
        df["ReuseMethod"].str.count(pat="Conceptual").sum().__int__()
    )
    data["Adaptation"] = (
        df["ReuseMethod"].str.count(pat="Adaptation").sum().__int__()
    )
    data["Deployment"] = (
        df["ReuseMethod"].str.count(pat="Deployment").sum().__int__()
    )

    print("Conceptual Reuse:", data["Conceptual"])
    print("Adaptation Reuse:", data["Adaptation"])
    print("Deployment Reuse:", data["Deployment"])


def countPapersPerReuseMethod(df: DataFrame) -> None:
    data: dict[str, int] = {
        "Conceptual": 0,
        "Adaptation": 0,
        "Deployment": 0,
        "Multiple": 0,
    }

    df = df.dropna(axis=0, subset="ReuseMethod")
    print("Papers With Reuse Method:", df.shape[0])

    data["Conceptual"] = df["ReuseMethod"].str.contains(pat="Conceptual").sum()
    data["Adaptation"] = df["ReuseMethod"].str.contains(pat="Adaptation").sum()
    data["Deployment"] = df["ReuseMethod"].str.contains(pat="Deployment").sum()

    row: Series
    for _, row in df.iterrows():
        record: str = row["ReuseMethod"]

        c: bool = True if record.find("Conceptual") > -1 else False
        a: bool = True if record.find("Adaptation") > -1 else False
        d: bool = True if record.find("Deployment") > -1 else False

        if c + a + d > 1:
            data["Multiple"] += 1

    print("Papers Using Conceptual Reuse:", data["Conceptual"])
    print("Papers Using Adaptation Reuse:", data["Adaptation"])
    print("Papers Using Deployment Reuse:", data["Deployment"])
    print("Papers Using Multiple Reuse Methods:", data["Multiple"])


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
    df: DataFrame = readDF(fp=slr)
    print("===")

    dlDF: DataFrame = countPapersThatUseDL(df=df)
    print("===")

    countReuseMethodsPerPaper(df=dlDF)
    print("===")

    countPapersPerReuseMethod(df=dlDF)
    print("===")


if __name__ == "__main__":
    main()
