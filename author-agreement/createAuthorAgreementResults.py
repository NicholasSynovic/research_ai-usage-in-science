from collections import defaultdict
from pathlib import Path
from typing import Any, List

import click
import pandas
from pandas import DataFrame, ExcelFile
from pandas.core.groupby import DataFrameGroupBy


def createBaseDF(df: DataFrame) -> DataFrame:
    data: List[dict[str, Any]] = []

    dfgb: DataFrameGroupBy = df.groupby(by="Paper DOI\n")

    doi: str
    _df: DataFrame
    for doi, _df in dfgb:
        datum: defaultdict[str, str | bool | None] = defaultdict(None)
        datum["doi"] = doi.strip()

        dlUsage: List[str] = _df[
            "Do The Author's Use Deep Learning?\n"
        ].unique()

        if len(dlUsage) == 1:
            datum["uses_dl"] = True if dlUsage[0] == "Yes" else False
        else:
            datum["uses_dl"] = False

        data.append(datum)

    return DataFrame(data=data)


@click.command()
@click.option(
    "-i",
    "--input",
    "inputFP",
    help="Path to input file",
    type=click.Path(
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
    required=True,
)
def main(inputFP: Path) -> None:
    excelFile: ExcelFile = ExcelFile(path_or_buffer=inputFP, engine="openpyxl")
    excelDF: DataFrame = pandas.read_excel(io=excelFile, sheet_name="Form1")

    df: DataFrame = createBaseDF(df=excelDF)
    print(df)


if __name__ == "__main__":
    main()
