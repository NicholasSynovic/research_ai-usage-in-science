"""
Read in PDF text, format with `mdformat` and tokenize with `tiktoken`.
Store the file path, text, tokenized text, and token count in a parquet file
"""

from argparse import ArgumentParser, Namespace
from os import listdir
from pathlib import Path

import pandas
from langchain_community.document_loaders import PyPDFLoader
from pandas import DataFrame
from progress.bar import Bar

PROGRAM_NAME: str = "PDF preprocessor"


def cli() -> Namespace:
    parser: ArgumentParser = ArgumentParser(prog=PROGRAM_NAME)

    parser.add_argument(
        "-d",
        "--directory",
        type=lambda x: Path(x).resolve(),
        nargs=1,
        required=True,
        help="Path to PDF directory",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=lambda x: Path(x).resolve(),
        nargs=1,
        required=True,
        help="Path to store output as an Apache Parquet file",
    )

    return parser.parse_args()


def get_paths(directory: Path) -> list[Path]:
    files: list[str] = listdir(path=directory)
    return [Path(directory, file) for file in files]


def process_pdf(pdf_path: Path) -> DataFrame:
    data: dict[str, list] = {
        "filename": [pdf_path.name],
        "document_text": [],
    }
    pdf_loader: PyPDFLoader = PyPDFLoader(
        file_path=pdf_path,
        extract_images=False,
        mode="single",
    )
    data["document_text"].append(pdf_loader.load()[0].page_content)

    return DataFrame(data=data)


def main() -> None:
    args: Namespace = cli()

    filepaths: list[Path] = get_paths(directory=args.directory[0])

    df_list: list[DataFrame] = []
    with Bar("Preprocessing PDFs... ", max=len(filepaths)) as bar:
        filepath: Path
        for filepath in filepaths:
            df_list.append(process_pdf(pdf_path=filepath))
            bar.next()

    df: DataFrame = pandas.concat(objs=df_list, ignore_index=True)
    df.to_parquet(path=args.output[0])


if __name__ == "__main__":
    main()
