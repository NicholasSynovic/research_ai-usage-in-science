import pickle
from pathlib import Path

import click
import pandas
from pandas import DataFrame, Series
from progress.bar import Bar
from requests import Response, post

CONTEXT_WNDOW_SIZE: int = 64926

SYSTEM_PROMPT: str = """
(C) Context:
You are an AI model integrated into an automated pipeline that processes academic computational Natural Science papers into a machine readable format.
Your sole responsibility is to evaluate the paper's content and determine whether the author's use deep learning models or methods in their methodology.
Your response will be consumed by downstream systems that require structured JSON.

(O) Objective:
Your task is to output only a JSON object containing a single key-value pair, where the key is "result" and the value is a boolean (true or false) based on whether the input text use deep learning models or methods in their methodology.
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


def load_parquet(fp: Path) -> DataFrame:
    # Read file contents from Apache Parquet file
    return pandas.read_parquet(path=fp, engine="pyarrow")


def compute_context_window_size(df: DataFrame) -> int:
    return df["tokens"].max() + 1000


def query_ollama(
    text: str,
    model: str,
    ollama_api: str,
) -> Response:
    return post(
        url=f"http://{ollama_api}/api/generate",
        timeout=360000,
        json={
            "model": model,
            "stream": False,
            "prompt": text,
            "system": SYSTEM_PROMPT,
            "options": {
                "temperature": 0.1,
                "top_k": 1,
                "top_p": 0.1,
                "num_predict": 10,
                "num_ctx": CONTEXT_WNDOW_SIZE,
                "seed": 42,
            },
        },
    )


@click.command()
@click.option(
    "-i",
    "--input-path",
    help="Path to formatted Markdown Apache Parquet file",
    type=lambda x: Path(x).resolve(),
)
@click.option(
    "-o",
    "--output-path",
    help="Path to write output JSON file",
    type=lambda x: Path(x).resolve(),
)
@click.option(
    "-m",
    "--model",
    help="LLM to use for analysis",
    type=click.Choice(
        choices=[
            "gpt-oss:20b",
            "deepseek-r1:70b",
            "gemma3:27b",
            "llama4:16x17b",
            "gemma3:4b",
        ],
        case_sensitive=True,
    ),
    default="gemma3:4b",
    show_default=True,
)
@click.option(
    "--ollama-api",
    help="Ollama API URL",
    type=str,
    default="localhost:11434",
    show_default=True,
)
def main(
    input_path: Path,
    output_path: Path,
    model: str,
    ollama_api: str,
) -> None:
    data: list[tuple[str, Response]] = []

    df: DataFrame = load_parquet(fp=input_path)

    with Bar("Running analysis...", max=df.shape[0]) as bar:
        row: Series
        for _, row in df.iterrows():
            resp: Response = query_ollama(
                text=repr(row["content"]),
                model=repr(model),
                ollama_api=ollama_api,
            )
            data.append((row["filename"], resp))
            bar.next()

    with open(file=output_path, mode="wb") as pf:
        pickle.dump(obj=data, file=pf)
        pf.close()


if __name__ == "__main__":
    main()
