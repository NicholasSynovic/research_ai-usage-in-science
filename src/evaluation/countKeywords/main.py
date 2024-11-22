import re
from pathlib import Path
from typing import List

import click
import pandas
from pandas import DataFrame
from tqdm import tqdm

from src.classes import SEARCH_QUERIES
from src.utils import ifFileExistsExit


def createFuzzyRegex(keyword: str) -> str:
    escapedKeyword: str = re.escape(keyword)
    # looks for escaped space character in keyword, allowing then any characters between words to provide a match, the ? makes it non greedy # noqa: E501
    fuzzyPattern: str = re.sub(r"\\ ", r".*?", escapedKeyword)
    return fuzzyPattern


# def countKeywords(df: DataFrame, keywords: List[str]) -> DataFrame:
#     data: dict[str, List[int]] = {kw: [] for kw in keywords}
#     data["doi"] = []


#     with Bar("Counting keywords...", max=df.shape[0]) as bar:
#         row: Series[str]
#         for _, row in df.iterrows():
#             data["doi"].append(row["doi"])

#             title: str = row["titles"].lower()
#             abstract: str = row["abstracts"].lower()
#             content: str = row["content"].lower()

#             for kw, pattern in fuzzyPatterns.items():

#                 count: int = 0

#                 count += len(list(pattern.finditer(title)))
#                 count += len(list(pattern.finditer(abstract)))
#                 count += len(list(pattern.finditer(content)))

#                 data[kw].append(count)

#             bar.next()

#     return DataFrame(data=data)


# new
def countKeywords(df: DataFrame, keywords: List[str]) -> DataFrame:
    # Initialize dictionary to store counts
    data: dict[str, int] = {kw: 0 for kw in keywords}

    # Create regex patterns for fuzzy keyword matching
    fuzzyPatterns = {
        kw: re.compile(createFuzzyRegex(kw), re.IGNORECASE) for kw in keywords
    }

    # Progress bar for iteration
    tqdm.pandas(desc="Counting papers with keywords...")

    def check_keywords(row):
        title: str = row["titles"].lower()
        abstract: str = row["abstracts"].lower()
        content: str = row["content"].lower()

        for kw, pattern in fuzzyPatterns.items():
            if (
                pattern.search(title)
                or pattern.search(abstract)
                or pattern.search(content)
            ):
                data[kw] += 1

    # Iterate over rows to count papers with keywords
    df.progress_apply(check_keywords, axis=1)

    # Convert results to a DataFrame
    result_df = DataFrame(
        list(data.items()), columns=["Keyword", "Paper Count"]
    )

    return result_df


@click.command()
@click.option(
    "-i",
    "--input",
    "inputPath",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
    required=True,
    help="Path to a transformed set of papers",
)
@click.option(
    "-o",
    "--output",
    "outputPath",
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        readable=False,
        resolve_path=True,
        path_type=Path,
    ),
    required=True,
    help="Path to store data in CSV format",
)
def main(inputPath: Path, outputPath: Path) -> None:
    # 1. Check if output path already exists
    ifFileExistsExit(fps=[outputPath])

    # 2. Format keywords
    keywords: List[str] = [kw.strip('"').lower() for kw in SEARCH_QUERIES]

    # 3. Read in transformed documents
    print(f'Reading "{inputPath}"...')
    df: DataFrame = pandas.read_parquet(path=inputPath, engine="pyarrow")

    # 4. Count keywords
    ckDF: DataFrame = countKeywords(df=df, keywords=keywords)

    # 5. Write results
    print(f'Writing "{outputPath}"...')
    ckDF.to_csv(path_or_buf=outputPath, index=False)


if __name__ == "__main__":
    main()
