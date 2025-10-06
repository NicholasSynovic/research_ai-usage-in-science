from json import loads
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import Any

import click
import pandas
from pandas import DataFrame, Series
from progress.bar import Bar
from prompts import *
from requests import Response, post

CONTEXT_WNDOW_SIZE: int = 64926
POST_TIMEOUT: int = 360000


def set_system_prompt(prompt_choice: str) -> str:
    # Identify system prompt to use
    system_prompt: str = ""
    match prompt_choice:
        case "uses-dl":
            system_prompt = USES_DEEP_LEARNING_PROMPT
        case "uses-ptms":
            system_prompt = USES_PTMS_PROMPT
        case "identify-ptms":
            system_prompt = IDENTIFY_PTMS_PROMPT
        case "usage-method":
            system_prompt = PMT_REUSE_METHOD_PROMPT

    return system_prompt


def set_json_formatting(model: str) -> bool:
    # Identify how to handle JSON responses based on models
    json_format: bool = True
    match model:
        case "gpt-oss:20b":
            json_format = False
        case "deepseek-r1:70b":
            json_format = False
        case _:
            json_format = True

    return json_format


def load_parquet(fp: Path) -> DataFrame:
    # Read file contents from Apache Parquet file
    return pandas.read_parquet(path=fp, engine="pyarrow")


def compute_context_window_size(df: DataFrame) -> int:
    # Add 1000 tokens to the context window based off of the largest document
    # (by token count)
    return df["tokens"].max() + 1000


def query_ollama(
    text: str,
    model: str,
    ollama_api: str,
    system_prompt: str,
    json_format: bool = True,
) -> Response:
    url: str = f"http://{ollama_api}/api/generate"

    json_data: dict = {
        "model": model,
        "stream": False,
        "prompt": text,
        "system": system_prompt,
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
    "-p",
    "--prompt-choice",
    help="System prompt selection",
    type=click.Choice(
        choices=[
            "uses-dl",
            "uses-ptms",
            "identify-ptms",
            "usage-method",
        ],
        case_sensitive=True,
    ),
    default="uses-dl",
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
    prompt_choice: str,
) -> None:
    # Setup storage data structure
    data: dict[str, list[str | Response | dict[str, Any]]] = {
        "filename": [],
        "response_obj": [],
        "json": [],
    }

    # Set the JSON formatting flag
    json_formatting: bool = set_json_formatting(model=model)

    # Set the system prompt
    system_prompt: str = set_system_prompt(prompt_choice=prompt_choice)

    # Load data
    input_df: DataFrame = load_parquet(fp=input_path)

    # Run analysis

    with Bar("Running analysis...", max=input_df.shape[0]) as bar:
        row: Series
        for _, row in input_df.iterrows():
            # Get text from DataFrame row
            text: str = row["content"]

            # Query Ollama API
            resp: Response = query_ollama(
                text=text,
                model=model,
                ollama_api=ollama_api,
                system_prompt=system_prompt,
                json_format=json_formatting,
            )

            # Handle response
            data["filename"].append(row["filename"])
            data["response_obj"].append(resp)

            try:
                if json_formatting:
                    data["json"].append(loads(s=resp.json()["response"]))
                else:
                    data["json"].append({})
            except JSONDecodeError:
                data["json"].append({})

            bar.next()

    # Write data to Python pickle file
    DataFrame(data=data).to_pickle(path=output_path)


if __name__ == "__main__":
    main()
