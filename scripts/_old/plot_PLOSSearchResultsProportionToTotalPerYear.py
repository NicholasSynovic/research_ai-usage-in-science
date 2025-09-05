from typing import List

import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from pandas import DataFrame, Series, Timestamp

PAPERS_PER_YEAR: dict[int, int] = {
    2014: 35356,
    2015: 33446,
    2016: 26640,
    2017: 24516,
    2018: 22122,
    2019: 19632,
    2020: 20426,
    2021: 20840,
    2022: 20631,
    2023: 19682,
    2024: 16278,
}

# 2024 count from 9-20-2024


def computeProportion(vc: Series) -> dict[int, float]:
    totalPapers: List[int] = list(PAPERS_PER_YEAR.values())
    years: List[int] = list(PAPERS_PER_YEAR.keys())

    proportions: dict[int, float] = {}

    value: int
    for value in vc:
        proportions[years.pop(0)] = (value / totalPapers.pop(0)) * 100

    return proportions


def plot(proportions: dict[int, float]) -> None:
    years: List[int] = list(proportions.keys())

    sns.barplot(data=proportions)
    plt.title(
        label="Proportion Of Deep Learning Search Results\nTo Total Papers Published In PLOS"  # noqa:E501
    )
    plt.xlabel(xlabel="Year")
    plt.ylabel(ylabel="Proportion")

    idx: int
    for idx in range(len(years)):
        value: float = proportions[years[idx]]
        plt.text(
            x=idx,
            y=value + 0.1,
            s=("%.3f" % value),
            ha="center",
            size="small",
        )

    plt.tight_layout()
    plt.savefig("proportions.png")


def main() -> None:
    df: DataFrame = pandas.read_parquet(
        path="../data/plos/plos_documents.parquet",
        engine="pyarrow",
    )

    df["year"] = df["publication_date"].apply(lambda x: Timestamp(x).year)

    yearCounts: Series = df["year"].value_counts(ascending=True)

    data: dict[int, float] = computeProportion(vc=yearCounts)

    plot(proportions=data)


if __name__ == "__main__":
    main()
