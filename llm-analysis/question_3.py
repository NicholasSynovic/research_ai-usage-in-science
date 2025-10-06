from json import loads
from pathlib import Path

import click
import pandas
from pandas import DataFrame, Series
from progress.bar import Bar
from requests import Response, post

CONTEXT_WNDOW_SIZE: int = 64926
POST_TIMEOUT: int = 360000

SYSTEM_PROMPT: str = """
(C) Context:
You are an AI model integrated into an automated pipeline that processes academic Computational Natural Science papers into a machine-readable format.
Your sole responsibility is to evaluate the paper's content and identify every instance where the authors use pre-trained deep learning models (PTMs).
For each identified PTM, you must determine which reuse method the authors employ.
Your response will be consumed by downstream systems that require structured JSON.

(O) Objective:
Your task is to output only a JSON array, where each element is an object containing the following key-value pairs:
- "model" — a string specifying the name or type of the pre-trained deep learning model (PTM) mentioned,
- "reuse_method" — a string specifying which of the following reuse methods best describes how the PTM is leveraged, and
- "prose" — the most salient excerpt from the paper that demonstrates and supports your classification.

Reuse method definitions (for disambiguation):
- Conceptual Reuse: The authors replicate, reimplement, or reengineer algorithms, model architectures, or conceptual designs based on published PTMs or their academic descriptions, integrating those reconstructed concepts into their own models or workflows. No direct reuse of weights or models occurs—only the conceptual or architectural ideas are reused.
- Adaptation Reuse: The authors directly reuse a pre-trained model's parameters or architecture and adapt or fine-tune it to a new dataset, task, or domain. The PTM serves as a base model that is modified or retrained for a different purpose.
- Deployment Reuse: The authors use an existing pre-trained model as-is, possibly converting or integrating it into a new computational framework, platform, or environment (e.g., ONNX, TensorRT, cloud inference service), without modifying its parameters or retraining.

If no PTMs or reuse methods are detected, return an empty JSON array.
No explanations, comments, or extra output are allowed.

(S) Style:
Responses must be strictly machine-readable JSON.
No natural language, commentary, or formatting beyond the JSON array is permitted.

(T) Tone:
Neutral, objective, and machine-like.

(A) Audience:
The audience is a machine system that parses JSON.
Human readability is irrelevant.

(R) Response:
Return only a JSON array of the form:

[
    {
        "model": String,
        "reuse_method": "Conceptual Reuse" | "Adaptation Reuse" | "Deployment Reuse",
        "prose": String
    },
    ...
]

If no PTMs are detected, return:

[]

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
    json_format: bool = True,
) -> Response:
    url: str = f"http://{ollama_api}/api/generate"

    json_data: dict = {
        "model": model,
        "stream": False,
        "prompt": text,
        "system": SYSTEM_PROMPT,
        "keep_alive": "30m",
        "options": {
            "temperature": 0.1,
            "top_k": 1,
            "top_p": 0.1,
            "num_predict": 1000,
            "num_ctx": CONTEXT_WNDOW_SIZE,
            "seed": 42,
        },
    }

    if json_format:
        json_data["format"] = "json"

    return post(url=url, timeout=POST_TIMEOUT, json=json_data)


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
    help="Path to write output pickle file",
    type=lambda x: Path(x).resolve(),
)
@click.option(
    "-m",
    "--model",
    help="LLM to use for analysis",
    type=click.Choice(
        choices=[
            "granite3.3:8b",
            "phi3:14b",
            "gemma3:27b",
            "gpt-oss:20b",
            "magistral:24b",
            "deepseek-r1:70b",
            "llama4:16x17b",
        ],
        case_sensitive=True,
    ),
    default="gemma3:27b",
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
    data: dict[str, list[str | Response]] = {
        "filename": [],
        "response_obj": [],
        "json": [],
    }

    input_df: DataFrame = load_parquet(fp=input_path)

    with Bar("Running analysis...", max=input_df.shape[0]) as bar:
        row: Series
        for _, row in input_df.iterrows():
            resp: Response = query_ollama(
                text=row["content"],
                model=model,
                ollama_api=ollama_api,
                json_format=False if model == "gpt-oss:20b" else True,
            )
            data["filename"].append(row["filename"])
            data["response_obj"].append(resp)
            data["json"].append(loads(s=resp.json()["response"]))

            bar.next()

    output_df: DataFrame = DataFrame(data=data)
    output_df.to_pickle(path=output_path)


if __name__ == "__main__":
    main()
