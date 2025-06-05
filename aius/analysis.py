from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame, Series

from aius.db import DB


def countTotalSearchResultsFromPLOS(db: DB) -> int:
    """
    Total search results from PLOS.
    """
    df: DataFrame = db.getPLOSPapersPerKeyword()
    data: int = df["keyword"].count()
    return data


def countTotalUniqueSearchResultsFromPLOS(db: DB) -> int:
    """
    Total unique search results from PLOS.
    The first entry is always kept.
    """
    df: DataFrame = db.getPLOSPapersPerKeyword()
    df.drop_duplicates(subset="document_id", keep="first", inplace=True)
    data: int = df["keyword"].count()
    return data


def countTotalCompletelyUniqueSearchResultsFromPLOS(db: DB) -> int:
    """
    Total completely unique search results from PLOS.
    No duplicates are kept.
    """
    df: DataFrame = db.getPLOSPapersPerKeyword()
    df.drop_duplicates(subset="document_id", keep=False, inplace=True)
    data: int = df["keyword"].count()
    return data


def countTotalSearchResultsFromPLOSByKeyword(db: DB) -> Series:
    """
    Total search results from PLOS by keyword.
    """
    df: DataFrame = db.getPLOSPapersPerKeyword()
    data: Series = df["keyword"].value_counts()
    return data.sort_index()


def countTotalUniqueSearchResultsFromPLOSByKeyword(db: DB) -> Series:
    """
    Total unique search results from PLOS by keyword.
    The first entry is always kept.
    """
    df: DataFrame = db.getPLOSPapersPerKeyword()
    df.drop_duplicates(subset="document_id", keep="first", inplace=True)
    data: Series = df["keyword"].value_counts()
    return data.sort_index()


def countTotalCompletelyUniqueSearchResultsFromPLOSByKeyword(db: DB) -> Series:
    """
    Total unique search results from PLOS by keyword.
    The first entry is always kept.
    """
    df: DataFrame = db.getPLOSPapersPerKeyword()
    df.drop_duplicates(subset="document_id", keep=False, inplace=True)
    data: Series = df["keyword"].value_counts()
    return data.sort_index()


def countNumberOfPLOSPapersPerYear(db: DB) -> Series:
    """
    Total unique search results from PLOS by year published.
    The first entry is always kept.
    """
    df: DataFrame = db.getPLOSPapersPerYear()
    df.drop_duplicates(subset="document_id", keep="first", inplace=True)
    data: Series = df["year"].value_counts()
    return data.sort_index()


def countNumberOf_PLOS_OA_PapersPerYear(db: DB) -> Series:
    """
    Total unique search results from PLOS that were indexed by OpenAlex by year.
    The first entry is always kept.
    """  # noqa: E501
    df: DataFrame = db.get_PLOS_OA_PapersPerYear()
    df.drop_duplicates(subset="document_id", keep="first", inplace=True)
    data: Series = df["year"].value_counts()
    return data.sort_index()


def countNumberOf_PLOS_OA_NS_PapersPerYear(db: DB) -> None:
    """
    Total unique search results from PLOS that were indexed by OpenAlex, have at least one citation, and were classified as Natural Science.
    The first entry is always kept.
    """  # noqa: E501
    df: DataFrame = db.get_PLOS_OA_NS_PapersPerYear()
    df.drop_duplicates(subset="document_id", keep="first", inplace=True)
    data: Series = df["year"].value_counts()
    return data.sort_index()


def plotNumberOf_PLOS_OA_NS_PapersPerYear(db: DB, outputDir: Path) -> None:
    outputFP: Path = Path(outputDir, "fig_section-4.1.2.pdf")

    plosPapers: Series = countNumberOfPLOSPapersPerYear(db=db)
    nsPapers: Series = countNumberOf_PLOS_OA_NS_PapersPerYear(db=db)

    sns.barplot(
        x=plosPapers.index,
        y=plosPapers.values,
        label="PLOS Papers",
        order=plosPapers.index,
    )

    for i, v in enumerate(plosPapers.values):
        plt.text(
            i,
            v + 0.5,
            str(v),
            ha="center",
            va="bottom",
            fontsize="small",
        )

    sns.barplot(
        x=nsPapers.index,
        y=nsPapers.values,
        label="OpenAlex Indexed Natural Science PLOS Papers",
        order=nsPapers.index,
    )

    for i, v in enumerate(nsPapers.values, start=0):
        plt.text(
            i,
            v - (v * 0.50),
            str(v),
            ha="center",
            va="bottom",
            color="w",
            fontsize="small",
        )

    plt.title(
        label="Comparison Of Total Unique PLOS And\nOpenAlex Indexed Natural Science Papers"  # noqa: E501
    )

    plt.ylabel(ylabel="Number Of Papers")
    plt.xlabel(xlabel="Year")
    plt.tight_layout()
    plt.savefig(outputFP)
    plt.clf()

    print("Saved figure to:", outputFP)
