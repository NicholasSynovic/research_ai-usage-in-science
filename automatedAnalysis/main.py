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
def main(inputFP: Path, model: str, promptStr: str) -> None:
    ollamaAPI: str = "http://localhost:11434"

    loader: PyPDFLoader = PyPDFLoader(file_path=inputFP.__str__())
    documents: List[Document] = loader.load()

    jsonData: dict = {
        "model": model,
        "stream": False,
        "keep_alive": 0,
        "options": {
            "temperature": 0.1,
            "top_k": 1,
            "top_p": 0.1,
            "num_predict": 10,
            "num_ctx": 64000,
        },
        "messages": [
            {
                "role": "system",
                "content": "Respond either 'yes' or 'no' do not ",
            },
            {"role": "user", "content": f"{promptStr}\n\n{documents}"},
        ],
    }

    resp: Response = post(
        url=f"{ollamaAPI}/api/chat",
        json=jsonData,
        timeout=60,
    )

    print(resp.content)


if __name__ == "__main__":
    main()
