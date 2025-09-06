from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents.base import Document
from requests import Response, post

PROGRAM_NAME: str = '"Do the author\'s use deep learning?"'


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

    return parser.parse_args()


def main() -> None:
    pass


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
