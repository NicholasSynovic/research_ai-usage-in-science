from pathlib import Path
from typing import List

import click
import pandas
from fuzzywuzzy import fuzz, process
from pandas import DataFrame, Series
from progress.bar import Bar

from src.classes import SEARCH_QUERIES
from src.utils import ifFileExistsExit


# did not work as well as original regex method, almost no matches are found
def findFuzzyMatches(keyword: str, text: str) -> int:
    # similarity threshold that corresponds to an edit distance of up to 3
    similarityThreshold = 85

    words = text.split()

    matches = process.extract(keyword, words, scorer=fuzz.ratio)

    # count the number of matches that are above threshold
    count = sum(1 for match in matches if match[1] >= similarityThreshold)

    return count


def countKeywords(df: DataFrame, keywords: List[str]) -> DataFrame:
    data: dict[str, List[int]] = {kw: [] for kw in keywords}
    data["doi"] = []

    with Bar("Counting keywords...", max=df.shape[0]) as bar:
        row: Series[str]
        for _, row in df.iterrows():
            data["doi"].append(row["doi"])

            title: str = row["titles"].lower()
            abstract: str = row["abstracts"].lower()
            content: str = row["content"].lower()

            for kw in keywords:
                count: int = 0

                count += findFuzzyMatches(kw, title)
                count += findFuzzyMatches(kw, abstract)
                count += findFuzzyMatches(kw, content)

                data[kw].append(count)

            bar.next()

    return DataFrame(data=data)


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
