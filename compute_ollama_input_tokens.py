"""
Compute the total number of tokens per PDF document with Ollama.

Copyright 2025 (C) Nicholas M. Synovic

"""

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents.base import Document
from requests import Response, post
from argparse import ArgumentParser, Namespace
from progress.bar import Bar
from functools import partial
from pandas import DataFrame
import sys
from collections.abc import Generator


def cli() -> Namespace:
    """
    Parse command-line arguments for processing PDF files with an Ollama model.

    This function sets up an argument parser with several options related to PDF
    processing and Ollama model configuration. It returns the parsed arguments as
    a Namespace object.

    Args:
        -i, --input (Path): Path to the input PDF file directory. This argument is
            required.
        -m, --model (str): Model to use with Ollama. Defaults to "gemma3:latest".
        -o, --ollama (str): Ollama API endpoint. Defaults to "http://localhost:11434".
        -t, --timeout (int): Timeout for the Ollama API endpoint. Defaults to
            360 seconds.
        --context-token-limit (int): Limit the number of tokens a model is allowed in
            its context. Defaults to 128000.

    Returns:
        Namespace: A Namespace object containing the parsed command-line arguments.

    """
    parser: ArgumentParser = ArgumentParser(description="Process PDF with Ollama model")

    parser.add_argument(
        "-i",
        "--input",
        help="Path to input PDF file directory",
        required=True,
        type=Path,
    )
    parser.add_argument(
        "-m",
        "--model",
        help="Model to use with Ollama",
        default="gemma3:latest",
        type=str,
        required=False,
    )
    parser.add_argument(
        "-o",
        "--ollama",
        help="Ollama API endpoint",
        default="http://localhost:11434",
        type=str,
        required=False,
    )
    parser.add_argument(
        "-t",
        "--timeout",
        help="Ollama API endpoint timeout",
        default=360,
        type=int,
        required=False,
    )
    parser.add_argument(
        "--context-token-limit",
        help="Limit the number of tokens a model is allowed in its context",
        default=128000,
        type=int,
        required=False,
    )

    return parser.parse_args()


def list_files(directory_path: Path) -> list[Path]:
    """
    List all files in the specified directory.

    This function generates a list of resolved file paths for all files
    located in the given directory. It uses the `iterdir` method to iterate
    over the directory contents.

    Args:
        directory_path (Path): The path to the directory whose files are to be listed.

    Returns:
        list[Path]: A list of resolved file paths within the specified directory.

    """
    filenames: Generator[Path, None, None] = directory_path.iterdir()

    # fn is an abbreviation of filename
    return [Path(directory_path, fn).resolve() for fn in filenames]


def load_pdf(fp: Path) -> str:
    """
    Load and extract text content from a PDF file.

    This function uses the PyPDFLoader to read a PDF file and extract its text
    content. It concatenates the content from all pages into a single string,
    replacing newline characters with spaces for cleaner formatting.

    Args:
        fp (Path): The file path to the PDF file to be loaded.

    Returns:
        str: A string containing the extracted text content from the PDF file.

    """
    loader: PyPDFLoader = PyPDFLoader(file_path=str(fp.resolve()))
    documents: list[Document] = loader.load()
    content_list: list[str] = [document.page_content for document in documents]

    return " ".join(content_list).replace("\n", " ")


def create_json_data(
    model: str,
    content: str,
    context_token_limit: int = 128000,
) -> dict:
    """
    Construct a JSON payload for the Ollama model API request.

    This function generates a dictionary containing the necessary parameters for
    a request to the Ollama model API, including model configuration and content
    to be processed.

    Args:
        model (str): The name of the model to use with Ollama.
        content (str): The content to be used as the prompt for the model.
        context_token_limit (int, optional): The maximum number of tokens allowed
            in the model's context. Defaults to 128000.

    Returns:
        dict: A dictionary representing the JSON payload for the API request.

    """
    return {
        "model": model,
        "stream": False,
        "prompt": content,
        "system": "",
        "options": {
            "temperature": 0.1,
            "top_k": 1,
            "top_p": 0.1,
            "num_predict": 0,
            "num_ctx": context_token_limit,
        },
    }


def post_request(ollama_url: str, json: dict, timeout: int = 360) -> Response:
    """
    Send a POST request to the Ollama API endpoint to generate data.

    Args:
        ollama_url (str): The base URL of the Ollama API endpoint.
        json (dict): The JSON payload to be sent in the request body.
        timeout (int, optional): The timeout duration for the request in seconds.
            Defaults to 360.

    Returns:
        Response: The HTTP response object returned by the request.

    """
    return post(
        url=f"{ollama_url}/api/generate",
        json=json,
        timeout=timeout,
    )


def main() -> None:
    """
    Execute the main workflow for computing prompt tokens of PDF files using Ollama.

    This function orchestrates the following steps:
    1. Parses command-line arguments to obtain configuration settings.
    2. Resolves the input path and verifies it is a directory.
    3. Lists PDF files in the specified directory and extracts their content.
    4. Generates JSON data for each PDF content using the specified model and context
        token limit.
    5. Submits the JSON data to the Ollama API and collects responses.
    6. Saves the collected response data to a CSV file.

    Workflow:
        - Resolves the input directory path and checks its validity.
        - Extracts content from each PDF file in the directory.
        - Generates JSON data for each PDF using the specified model and context token
            limit.
        - Submits the JSON data to the Ollama API endpoint and records the responses.
        - Outputs the responses to a CSV file named after the model with token
            information.

    Notes:
        - The function uses progress bars to indicate the status of each major step.
        - The CSV file is saved in the current working directory with the name format
            '{model}_tokens.csv'.

    """
    args: Namespace = cli()

    resolved_input_path: Path = args.input.resolve()
    if resolved_input_path.is_dir() is False:
        sys.exit(1)

    files: list[Path] = list_files(directory_path=resolved_input_path)

    pdf_content: list[str] = []
    file: Path
    with Bar("Extracting content from PDFs...", max=len(files)) as bar:
        for file in files:
            pdf_content.append(load_pdf(fp=file))
            bar.next()

    json_data_generation_func: partial = partial(
        create_json_data,
        model=args.model,
        context_token_limit=args.context_token_limit,
    )

    json_data: list[dict] = []
    content: str
    with Bar("Generating JSON data to send to Ollama...", max=len(pdf_content)) as bar:
        for content in pdf_content:
            json_data.append(json_data_generation_func(content=content))
            bar.next()

    responses: dict[str, list[str | int]] = {
        "pdf_path": [],
        "model": [],
        "context_token_limit": [],
        "response_code": [],
        "actual_context_tokens": [],
        "token_difference": [],
        "json": [],
    }
    json: dict
    with Bar("Submitting JSON data to Ollama...", max=len(json_data)) as bar:
        for json in json_data:
            responses["pdf_path"].append(str(files.pop(0)))
            responses["model"].append(args.model)
            responses["context_token_limit"].append(args.context_token_limit)

            resp: Response = post_request(
                ollama_url=args.ollama,
                json=json,
                timeout=args.timeout,
            )

            responses["response_code"].append(resp.status_code)
            responses["actual_context_tokens"].append(resp.json()["prompt_eval_count"])
            responses["json"].append(resp.json())

            bar.next()

    data: DataFrame = DataFrame(data=responses)
    data.to_csv(path_or_buf=f"{args.model}_tokens.csv")


if __name__ == "__main__":
    main()
