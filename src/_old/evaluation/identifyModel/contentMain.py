from pathlib import Path
from typing import List

import click
import pandas
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama.llms import OllamaLLM


def identifyModel(inputPath: Path, outputPath: Path):
    df = pandas.read_parquet(inputPath)
    model: OllamaLLM = OllamaLLM(model="llama3.1")

    size = 3000

    parser: StrOutputParser = StrOutputParser()

    chain = model | parser

    results = []
    max_iterations = 5

    for i, row in enumerate(df.itertuples(index=False)):
        if i >= max_iterations:
            break

        doi = getattr(row, "doi", "n/a")

        content = getattr(row, "content", "n/a")

        chunks = [
            content[i : i + size]  # noqa: E203
            for i in range(0, len(content), size)
        ]

        list = []
        for chunk in chunks:
            promptTemplate: List = [
                SystemMessage(
                    content="""You are a deep learning model identifier for academic papers.
            Your task is to read the contents of an academic paper up until 'references' and extract the names of pre-trained models that occur in the paper.
            Return only the name(s) of the models. If there are none, return 😞.
            You keep responses concise without any extra information.
            """  # noqa: E501
                ),
                HumanMessage(content=chunk),
            ]

            parser: StrOutputParser = StrOutputParser()
            # parser = JsonOutputParser()

            chain = model | parser
            resp: str = chain.invoke(input=promptTemplate)
            list.append(resp)

        combined_results = "\n".join(list)
        combined_results = combined_results.replace("\n", " ").strip()

        results.append(
            {"doi": doi, "prompt": content, "response": combined_results}
        )

    resultsDF = pandas.DataFrame(results)

    resultsDF.to_csv(outputPath, index=False)


@click.command()
@click.option(
    "-i",
    "--input",
    "inputPath",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        path_type=Path,
    ),
    required=True,
    help="Path to a transformed set of papers",
)
@click.option(
    "-o",
    "--output",
    "outputPath",
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        readable=False,
        resolve_path=True,
        path_type=Path,
    ),
    required=True,
    help="Path to store data in CSV format",
)
def main(inputPath: Path, outputPath: Path) -> None:
    identifyModel(inputPath, outputPath)


if __name__ == "__main__":
    main()
