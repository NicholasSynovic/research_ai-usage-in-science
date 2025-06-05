from pathlib import Path

import click
import pandas
from bs4 import BeautifulSoup
from pandas import DataFrame, Series
from progress.bar import Bar
from pyfs import isDirectory, isFile, resolvePath


@click.command()
@click.option(
    "-i",
    "--input",
    "inputPath",
    required=True,
    type=Path,
    help="Path to parquet file to create HTML documents from",
)
@click.option(
    "-o",
    "--output",
    "outputPath",
    required=True,
    type=Path,
    help="Path to a directory to save HTML documents to",
)
def main(inputPath: Path, outputPath: Path) -> None:
    """
    Main function to read a Parquet file, process its contents, and generate HTML files.

    This function performs the following steps:
    1. Resolves the input and output paths.
    2. Checks if the input path points to a valid file and the output path points to a valid directory.
    3. Reads a Parquet file into a DataFrame.
    4. Iterates over the DataFrame rows and creates an HTML file for each row using BeautifulSoup to prettify the HTML content.
    5. Displays a progress bar indicating the creation of HTML files.

    :param inputPath: The path to the input Parquet file.
    :type inputPath: Path
    :param outputPath: The path to the directory where HTML files will be saved.
    :type outputPath: Path
    """  # noqa: E501
    absInputPath: Path = resolvePath(path=inputPath)
    absOutputPath: Path = resolvePath(path=outputPath)

    if isFile(path=absInputPath) is False:
        print(f"{absInputPath} is not a file")
        exit(1)

    if isDirectory(path=absOutputPath) is False:
        print(f"{absOutputPath} is not a directory")
        exit(1)

    df: DataFrame = pandas.read_parquet(path=absInputPath, engine="pyarrow")

    with Bar("Creating HTML files...", max=df.shape[0]) as bar:
        row: Series
        for _, row in df.iterrows():
            filepath: Path = Path(
                absOutputPath,
                f"{row['year']}_{row['query']}_{row['page']}_{row['status_code']}.html",  # noqa: E501
            )

            soup: BeautifulSoup = BeautifulSoup(
                markup=row["html"],
                features="lxml",
            )

            with open(file=filepath, mode="w") as htmlFile:
                htmlFile.write(soup.prettify())
                htmlFile.close()

            bar.next()


if __name__ == "__main__":
    main()
