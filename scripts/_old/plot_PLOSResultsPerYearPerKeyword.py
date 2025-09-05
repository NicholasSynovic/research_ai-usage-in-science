from typing import List
from warnings import filterwarnings

import matplotlib.pyplot as plt
import pandas
from pandas import DataFrame, Series, Timestamp

filterwarnings(action="ignore")


def formatData(df: DataFrame) -> DataFrame:
    data: dict[str, List[str]] = {"year": []}

    foo: DataFrame = df[["publication_date", "queryURL"]]

    foo["year"] = df["publication_date"].apply(lambda x: Timestamp(x).year)
    foo["query"] = df["queryURL"].apply(
        lambda x: x.split("&")[-1].split("=")[-1].replace('"', "")
    )
    foo = foo.drop(columns=["publication_date", "queryURL"])

    data["year"] = foo["year"].unique().tolist()

    for query in foo["query"].unique():
        data[query] = []

    for year in data["year"]:
        bar: DataFrame = foo[foo["year"] == year]
        values: Series = bar["query"].value_counts()

        for query in foo["query"].unique():
            try:
                data[query].append(values[query])
            except KeyError:
                data[query].append(0)

    return DataFrame(data=data)


def main() -> None:
    df: DataFrame = pandas.read_parquet(
        path="../data/plos/plos_documents.parquet",
        engine="pyarrow",
    )

    dfData: DataFrame = formatData(df=df)

    dfData.plot(x="year")
    plt.title(label="Documents per Search Query per Year")
    plt.xlabel(xlabel="Year")
    plt.ylabel(ylabel="Document Count")
    plt.savefig("plot.png")

    print(dfData)


if __name__ == "__main__":
    main()
