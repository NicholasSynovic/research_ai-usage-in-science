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

PROGRAM_NAME: str = "Are pre-trained deep learning models used?"
SYSTEM_PROMPT: str = """
(C) Context:
You are an AI model integrated into an automated pipeline that processes academic computational Natural Science papers into a machine readable format.
Your sole responsibility is to evaluate the paper's content and determine whether the author's reuse pre-trained deep learning models in their methodology.
Your response will be consumed by downstream systems that require structured JSON.

(O) Objective:
Your task is to output only a JSON object containing a single key-value pair, where the key is "result" and the value is a boolean (true or false) based on whether the input text reuses pre-trained deep learning methods in their methodology.
No explanations or extra output are allowed.

(S) Style:
Responses must be strictly machine-readable JSON.
No natural language, commentary, or formatting beyond the JSON object is permitted.

(T) Tone:
Neutral, objective, and machine-like.

(A) Audience:
The audience is a machine system that parses JSON.
Human readability is irrelevant.

(R) Response:
Return only a JSON object of the form:

{"result": true}

or

{"result": false}

Nothing else should ever be returned.
"""
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
                    "seed": 42,
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
