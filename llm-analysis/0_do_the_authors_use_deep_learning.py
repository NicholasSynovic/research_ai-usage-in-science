import pickle
from json import dumps
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
Your task is to output only a JSON object containing a key-value pairs, where:
- the key "result" value is a boolean (true or false) based on whether the input text use deep learning models or methods in their methodology, and
- the key "pose" value is the most salient evidence of deep learning usage in the paper.
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

{
    "result": Boolean,
    "prose": String,
}

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
            "format": "json",
            "keep_alive": "30m",
            "options": {
                "temperature": 0.1,
                "top_k": 1,
                "top_p": 0.1,
                "num_predict": 1000,
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
    data: dict[str, list[str]] = {"filename": [], "json": []}

    input_df: DataFrame = load_parquet(fp=input_path)

    with Bar("Running analysis...", max=input_df.shape[0]) as bar:
        row: Series
        for _, row in input_df.iterrows():
            resp: Response = query_ollama(
                text=row["content"].strip("'"),
                model=model.strip("'"),
                ollama_api=ollama_api.strip("'"),
            )
            data["filename"].append(row["filename"])
            data["json"].append(dumps(obj=resp.json(), indent=4))

            bar.next()

    output_df: DataFrame = DataFrame(data=data)
    output_df.to_json(path_or_buf=output_path, indent=4)


if __name__ == "__main__":
    main()
