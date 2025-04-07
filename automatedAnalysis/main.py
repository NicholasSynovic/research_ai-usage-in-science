from pathlib import Path
from typing import List

import click
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.llms import Ollama
from langchain_core.documents.base import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence


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
    "prompt",
    help="User prompt to be provided with the documents",
    required=True,
    type=str,
)
def main(inputFP: Path, model: str, prompt: str) -> None:
    loader: PyPDFLoader = PyPDFLoader(file_path=inputFP.__str__())
    documents: List[Document] = loader.load()

    llm: Ollama = Ollama(base_url="http://localhost:11434", model=model)

    prompt_template: PromptTemplate = PromptTemplate(
        input_variables=["document"],
        template=prompt + ":\n{document}\nAnswer:",
    )

    chain: RunnableSequence = prompt_template | llm | StrOutputParser()

    resp: str = chain.invoke({"document": documents})

    print(resp)


if __name__ == "__main__":
    main()
