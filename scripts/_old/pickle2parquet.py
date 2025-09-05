from pathlib import Path

import click
import pandas
from pandas import DataFrame
from pyfs import isFile, resolvePath


def _exitIfFileDoesNotExist(path: Path) -> None:
    """
    Check if a given path points to a file, and exit if it does not.

    This function verifies whether the provided path points to an existing file.
    If the path does not point to a file, it prints an error message and exits
    the program with a status code of 1.

    :param path: The path to be checked.
    :type path: Path
    """  # noqa: E501
    if isFile(path=path) is False:
        print(f"{path} is not a file")
        exit(1)


@click.command()
@click.option(
    "-i",
    "--input",
    "inputPath",
    type=Path,
    required=True,
    help="Path to a pickled Pandas DataFrame object",
)
@click.option(
    "-o",
    "--output",
    "outputPath",
    type=Path,
    required=True,
    help="Path to save the Pandas DataFrame to a parquet file",
)
def main(inputPath: Path, outputPath: Path) -> None:
    """
    Main function to read a pickle file and convert it to a Parquet file.

    This function performs the following steps:
    1. Resolves the absolute paths for the input and output.
    2. Checks if the input path points to a valid file and the output path points to a valid directory.
    3. Reads a DataFrame from the input pickle file.
    4. Writes the DataFrame to the output path in Parquet format.

    :param inputPath: The path to the input pickle file.
    :type inputPath: Path
    :param outputPath: The path to the output directory where the Parquet file will be saved.
    :type outputPath: Path
    """  # noqa: E501
    absInputPath: Path = resolvePath(path=inputPath)
    absOutputPath: Path = resolvePath(path=outputPath)

    _exitIfFileDoesNotExist(path=absInputPath)
    _exitIfFileDoesNotExist(path=absOutputPath)

    print(f"Reading {absInputPath} ...")
    df: DataFrame = pandas.read_pickle(
        filepath_or_buffer=absInputPath,
    )  # nosec

    print(f"Writing {absOutputPath} ...")
    df.to_parquet(path=absOutputPath, engine="pyarrow")


if __name__ == "__main__":
    main()
