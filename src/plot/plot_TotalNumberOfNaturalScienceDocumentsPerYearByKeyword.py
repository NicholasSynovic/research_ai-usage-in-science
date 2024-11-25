from pathlib import Path
from typing import List

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
    data: List[dict[int, str | int]] = []

    documentsDF: DataFrame = pandas.read_parquet(
        path=inputPath,
        engine="pyarrow",
    )

    documentsDF["keyword"] = documentsDF["queryURL"].apply(
        lambda x: x.split("&")[3].replace("q=", "").replace('"', "")
    )

    documentsDF["publication_date"] = pandas.to_datetime(
        documentsDF["publication_date"]
    )

    documentsDFGB: DataFrameGroupBy = documentsDF.groupby(
        by=documentsDF["publication_date"].dt.year
    )

    idx: int
    _df: DataFrame
    for idx, _df in documentsDFGB:
        keywordsDFGB: DataFrameGroupBy = _df.groupby(by="keyword")
        for _keyword, _keywordDF in keywordsDFGB:
            data.append(
                {
                    "year": idx,
                    "amount": _keywordDF.shape[0],
                    "Keyword": _keyword,
                }
            )

    df: DataFrame = DataFrame(data=data)

    sns.barplot(data=df, x="year", y="amount", hue="Keyword")
    plt.title(
        label="Total Number of Natural Science PLOS Publications\nFrom Search Results by Keyword"  # noqa:E501
    )
    plt.xlabel(xlabel="Year")
    plt.ylabel(ylabel="Number of Publications")
    plt.tight_layout()

    plt.savefig(outputPath)


if __name__ == "__main__":
    main()
