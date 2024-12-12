from pathlib import Path
from typing import List

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
            "Paper Publication Date": "PubDate",
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

    df = df[
        df["OATF"].isin(
            [
                "Agricultural and Biological Sciences",
                "Environmental Science",
                "Neuroscience",
            ]
        )
    ]

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

    df["PubDate"] = pandas.to_datetime(df["PubDate"], format="%Y-%m-%d")

    dfgb: DataFrameGroupBy = df.groupby(by=df["PubDate"].dt.year)

    data: List[dict] = []

    _df: DataFrame
    for _, _df in dfgb:
        data.append(countReuseMethodsPerPaper(df=_df))

    dataDF: DataFrame = DataFrame(data=data)
    dataDF.index = dataDF.index + 2014

    sns.lineplot(data=dataDF)
    plt.title(label="DL Reuse Methods Per Year Of Top 3 Topics")
    plt.xlabel(xlabel="Year")
    plt.ylabel(ylabel="Count")
    plt.tight_layout()
    plt.savefig("Top3Topics_DLResuseMethodsPerYear_0.pdf")


if __name__ == "__main__":
    main()
