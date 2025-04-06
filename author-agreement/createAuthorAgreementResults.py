from collections import defaultdict
from pathlib import Path
from typing import Any, List

import click
import pandas
from pandas import DataFrame, ExcelFile, Series
from pandas.core.groupby import DataFrameGroupBy


def loadExcelFile(fp: Path, sheetName: str) -> DataFrame:
    ef: ExcelFile = ExcelFile(path_or_buffer=fp, engine="openpyxl")
    return pandas.read_excel(io=ef, sheet_name=sheetName)


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
            datum["uses_dl"] = None

        data.append(datum)

    return DataFrame(data=data)


def checkIfDLIsUsed(df: DataFrame, dlUsageDF: DataFrame) -> None:
    """
    Returns in-place modifications to `df`
    """
    idx: int
    row: Series
    for idx, row in df.iterrows():
        if row["uses_dl"] is None:
            doi: str = row["doi"]
            if dlUsageDF[dlUsageDF["DOIs"] == doi]["Nick"].values[0] is True:
                row["uses_dl"] = True
            else:
                row["uses_dl"] = False


@click.command()
@click.option(
    "-f",
    "--form-responses",
    "formResponsesFP",
    help="Path to form responses file",
    type=click.Path(
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
    required=True,
)
@click.option(
    "-0",
    "--dl-usage",
    "dlUsageFP",
    help="Path to author agreement file for 'Do the author's use DL?'",
    type=click.Path(
        exists=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
    required=True,
)
def main(formResponsesFP: Path, dlUsageFP: Path) -> None:
    currentExcelDF: DataFrame = loadExcelFile(
        fp=formResponsesFP,
        sheetName="Form1",
    )
    df: DataFrame = createBaseDF(df=currentExcelDF)

    currentExcelDF = loadExcelFile(
        fp=dlUsageFP,
        sheetName="Sheet1",
    )
    checkIfDLIsUsed(df=df, dlUsageDF=currentExcelDF)

    df.to_csv(path_or_buf="output.csv", index=False)


if __name__ == "__main__":
    main()
