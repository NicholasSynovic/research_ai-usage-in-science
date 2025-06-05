import re
import sys
from os.path import isfile
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List

# from pandas import DataFrame, Series
# from progress.bar import Bar

# from src.classes.journalGeneric import Journal_ABC


def ifFileExistsExit(fps: List[Path]) -> None:
    fp: Path
    for fp in fps:
        if isfile(path=fp):
            print(f'"{fp}" exists')
            sys.exit(1)


def formatText(string: str, stripNewLines: bool = True) -> str:
    string = re.sub(pattern=r"-\n", repl="", string=string)
    if stripNewLines:
        string = string.replace("\n", "")
        string = " ".join(string.split())

    return string


def storeStringInTempFile(string: str) -> str:
    tf: NamedTemporaryFile = NamedTemporaryFile(
        mode="w+t",
        delete=False,
    )

    tfName: str = tf.name

    tf.write(string)
    tf.close()

    return tfName


# def extractDOIsFromHTML(source: Journal_ABC, df: DataFrame) -> DataFrame:
#     data: dict[str, List[str | int]] = {
#         "urls": [],
#         "query": [],
#         "year": [],
#         "journal": [],
#     }

#     with Bar(
#         "Extracting paper URLs from search results...",
#         max=df.shape[0],
#     ) as bar:
#         row: Series
#         for _, row in df.iterrows():
#             urls: List[str] = source.extractPaperURLsFromSearchResult(
#                 respContent=row["html"]
#             )

#             url: str
#             for url in urls:
#                 data["urls"].append(url)
#                 data["query"].append(row["query"])
#                 data["year"].append(row["year"])
#                 data["journal"].append(row["journal"])

#             bar.next()

#         urlsDF: DataFrame = DataFrame(data=data)

#         urlsDF["urls"] = urlsDF["urls"].apply(
#             lambda x: f"https://doi.org/{source.extractDOIFromPaper(url=x)}"
#         )

#     return urlsDF
