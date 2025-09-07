import json
from argparse import ArgumentParser, Namespace
from pathlib import Path

import pandas
import tiktoken
from langchain_core.documents.base import Document
from pandas import DataFrame, Series
from progress.bar import Bar
from requests import Response, post
from tiktoken import Encoding

import aius

PROGRAM_NAME: str = '"Do the author\'s use deep learning?"'
SYSTEM_PROMPT: str = "You are part of a system that processes Boolean logic. For any question or statement, output only a machine-readable Boolean: True or False. No additional text, formatting, or explanation is allowed."
USER_PROMPT: str = PROGRAM_NAME


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
        help="Path to a directory to store output as JSON files",
    )

    parser.add_argument(
        "--ollama",
        type=str,
        nargs=1,
        required=True,
        help="Ollama API endpoint",
    )

    return parser.parse_args()


def compute_tokens(text: str) -> int:
    token_count: int = 127000

    encoding: Encoding = tiktoken.encoding_for_model("gpt-4")

    encoded_token_count: int = len(encoding.encode(text=text))
    if encoded_token_count < token_count:
        return encoded_token_count + 50

    return token_count


def main() -> None:
    args: Namespace = cli()

    df: DataFrame = pandas.read_parquet(path=args.pdf[0], engine="pyarrow")

    row: Series
    with Bar("Submitting requests...", max=df.shape[0]) as bar:
        for _, row in df.iterrows():
            fp: Path = Path(
                args.output[0],
                Path(row["filename"]).stem + ".json",
            )

            documents: list[Document] = row["document_text"]
            document_text: str = "".join(documents)
            prompt: str = f"{USER_PROMPT}\n\n{document_text}"

            jsonData: dict = {
                "model": args.model[0],
                "stream": False,
                "prompt": prompt,
                "system": SYSTEM_PROMPT,
                "options": {
                    "temperature": 0.1,
                    "top_k": 1,
                    "top_p": 0.1,
                    "num_predict": 10,
                    "num_ctx": 25000,
                },
            }

            resp: Response = post(
                url=f"http://{args.ollama[0]}/api/generate",
                json=jsonData,
                timeout=aius.GET_TIMEOUT,
            )

            fp.write_text(data=json.dumps(obj=resp.json(), indent=4))

            bar.next()


if __name__ == "__main__":
    main()
