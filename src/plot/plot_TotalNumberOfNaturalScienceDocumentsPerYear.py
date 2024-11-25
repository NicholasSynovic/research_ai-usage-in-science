from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from pandas import DataFrame
from pandas.core.groupby import DataFrameGroupBy


@click.command()
@click.option(
    "-i",
    "--input",
    "inputPath",
    nargs=1,
    required=True,
    help="Path to filtered journal documents from aius-filter-documents",
    type=click.Path(
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
)
@click.option(
    "-o",
    "--output",
    "outputPath",
    nargs=1,
    required=True,
    help="Path to write figure to",
    type=click.Path(
        exists=False,
        file_okay=True,
        writable=True,
        resolve_path=True,
        path_type=Path,
    ),
)
def main(inputPath: Path, outputPath: Path) -> None:
    data: dict[int, int] = {}

    df: DataFrame = pandas.read_parquet(
        path=inputPath,
        engine="pyarrow",
    )

    df["publication_date"] = pandas.to_datetime(df["publication_date"])

    dfgb: DataFrameGroupBy = df.groupby(by=df["publication_date"].dt.year)

    idx: int
    _df: DataFrame
    for idx, _df in dfgb:
        data[idx] = _df.shape[0]

    sns.barplot(data=data)
    plt.title(
        label="Total Number of Natural Science PLOS Publications From Search Results"  # noqa: E501
    )
    plt.xlabel(xlabel="Year")
    plt.ylabel(ylabel="Number of Publications")
    plt.tight_layout()

    plt.savefig(outputPath)


if __name__ == "__main__":
    main()
