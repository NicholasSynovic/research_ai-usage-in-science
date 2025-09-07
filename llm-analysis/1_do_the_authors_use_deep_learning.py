from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List

import pandas
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents.base import Document
from pandas import DataFrame
from requests import Response, post

PROGRAM_NAME: str = '"Do the author\'s use deep learning?"'


def cli() -> Namespace:
    parser: ArgumentParser = ArgumentParser(prog=PROGRAM_NAME)

    parser.add_argument(
        "-p",
        "--pdf",
        type=lambda x: Path(x).resolve(),
        nargs=1,
        required=True,
        help="Path to PDF preprocessing parquet file",
    )

    parser.add_argument(
        "-m",
        "--model",
        type=str.lower,
        nargs=1,
        required=True,
        help="Ollama LLM model",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=lambda x: Path(x).resolve(),
        nargs=1,
        required=True,
        help="Path to store output as an Apache Parquet file",
    )

    parser.add_argument(
        "--ollama",
        type=str,
        nargs=1,
        required=True,
        help="Ollama API endpoint",
    )

    return parser.parse_args()


def main() -> None:
    args: Namespace = cli()

    df: DataFrame = pandas.read_parquet(path=args.pdf[0], engine="pyarrow")
    print(df)


if __name__ == "__main__":
    main()


def main_old(
    inputFP: Path,
    model: str,
    promptStr: str,
    systemPromptStr: str,
    ollamaAPI: str,
    timeout: int,
    predictionTokens: int,
    contextTokens: int,
) -> None:
    loader: PyPDFLoader = PyPDFLoader(file_path=inputFP.__str__())
    documents: List[Document] = loader.load()

    jsonData: dict = {
        "model": model,
        "stream": False,
        "prompt": f"{promptStr}\n\n{documents}",
        "system": systemPromptStr,
        "options": {
            "temperature": 0.1,
            "top_k": 1,
            "top_p": 0.1,
            "num_predict": predictionTokens,
            "num_ctx": contextTokens,
        },
    }

    resp: Response = post(
        url=f"{ollamaAPI}/api/generate",
        json=jsonData,
        timeout=timeout,
    )

    print(
        "$MAGIC_VALUE_START$",
        inputFP.name,
        resp.json(),
        "$MAGIC_VALUE_END$",
    )
