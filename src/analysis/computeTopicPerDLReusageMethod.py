from pathlib import Path
from textwrap import wrap

import matplotlib.pyplot as plt
import numpy as np
import pandas
import seaborn as sns
from pandas import DataFrame
from pandas.core.groupby import DataFrameGroupBy

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
            "Open Alex Topic Fields": "OATF",
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

    df["OATF"] = df["OATF"].str.strip().str.split(pat=";")
    df.replace("", np.nan, inplace=True)

    df = df.explode(column="OATF", ignore_index=True)
    df.dropna(subset="OATF", inplace=True)

    return df


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

    return data


def main() -> None:
    df: DataFrame = readDF(fp=Path("../../data/slrData.xlsx"))
    dfgb: DataFrameGroupBy = df.groupby(by="OATF")

    data: dict[str, int] = {}

    SKIP: bool = True
    _df: DataFrame
    _id: str
    for _id, _df in dfgb:
        if SKIP:
            SKIP = False
        else:
            data[_id] = _df.value_counts(subset="ReuseMethod").sum()

    sns.barplot(data=data)
    plt.title("Reuse Method Count Per Topic")
    plt.xlabel(xlabel="OpenAlex Topic")
    plt.xticks(rotation=-45, ha="left")
    plt.ylabel(ylabel="DL Reusage Method Count")
    plt.tight_layout()
    plt.savefig("test.pdf")


if __name__ == "__main__":
    main()
