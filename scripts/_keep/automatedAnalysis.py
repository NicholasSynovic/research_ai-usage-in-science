from pathlib import Path
from typing import List

import click
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents.base import Document
from requests import Response, post


@click.command()
@click.option(
    "-i",
    "--input",
    "inputFP",
    help="Path to input PDF file",
    required=True,
    type=click.Path(
        exists=True,
        file_okay=True,
        resolve_path=True,
        path_type=Path,
    ),
)
@click.option(
    "-m",
    "--model",
    "model",
    help="Model to use with Ollama",
    required=False,
    default="gemma3:latest",
    show_default=True,
    type=str,
)
@click.option(
    "-p",
    "--prompt",
    "promptStr",
    help="User prompt to be provided with the documents",
    required=True,
    type=str,
)
@click.option(
    "-s",
    "--system-prompt",
    "systemPromptStr",
    help="System prompt to be provided with the documents",
    required=False,
    default="Respond either 'yes' or 'no'.",
    show_default=True,
    type=str,
)
@click.option(
    "-o",
    "--ollama",
    "ollamaAPI",
    help="Ollama API endpoint",
    required=False,
    default="http://localhost:11434",
    show_default=True,
    type=str,
)
@click.option(
    "-t",
    "--timeout",
    "timeout",
    help="Ollama API endpoint timeout",
    required=False,
    default=60,
    show_default=True,
    type=int,
)
@click.option(
    "--prediction-tokens",
    "predictionTokens",
    help="Number of tokens a model is allowed to generate in its predictions",
    required=False,
    default=10,
    show_default=True,
    type=int,
)
@click.option(
    "--context-tokens",
    "contextTokens",
    help="Number of tokens a model is allowed in its context",
    required=False,
    default=64000,
    show_default=True,
    type=int,
)
def main(
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

    print(inputFP.name, resp.json()["response"].lower())


if __name__ == "__main__":
    main()
