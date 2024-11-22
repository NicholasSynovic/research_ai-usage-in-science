import matplotlib.pyplot as plt
import pandas
import seaborn
from pandas import DataFrame


def plot(df: DataFrame) -> None:

    seaborn.set_theme(style="whitegrid")
    df = pandas.read_csv("pivotTable.csv", skiprows=1)

    # clean up csv file from pivot table
    df.columns = ["Year", "Adaptation", "Conceptual", "Deployment", "Total"]

    # filter/drop grand total row and total column
    df = df[df["Year"] != "Grand Total"]  #
    df = df.drop(columns=["Total"])

    # plot and skip year col
    plt.figure(figsize=(10, 6))
    for column in df.columns[1:]:
        x = df["Year"]
        y = df[column]
        plt.plot(x, y, marker="o", label=column)

    plt.xlabel("Year")
    plt.ylabel("Count")
    plt.title("Trends in Types of Reuse Over Time")
    plt.legend(title="Type of Reuse")

    # plt.show()


def main() -> None:
    df = pandas.read_csv("pivotTable.csv", skiprows=1)
    plot(df)
    plt.show()
