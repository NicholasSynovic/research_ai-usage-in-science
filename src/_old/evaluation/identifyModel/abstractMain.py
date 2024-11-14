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

    results = []
    max_iterations = 30

    parser: StrOutputParser = StrOutputParser()

    chain = model | parser

    for i, row in enumerate(df.itertuples(index=False)):
        if i >= max_iterations:
            break

        doi = getattr(row, "doi", "n/a")

        abstract = getattr(row, "abstracts", "n/a")

        promptTemplate: List = [
            SystemMessage(
                content="""You are a deep learning model identifier for academic papers.
        Your task is to extract the names of pre-trained models from paper abstracts alone.
        Return only the name of the identified model. If there are more than one, return them as a
        numbered list. If there are none, return 😞. You keep responses concise without any extra information.
        input: We adopted a pre-trained deep learning model (VGGFace) for AIFR on a dataset of 5,000 indigenous
                African faces (FAGE\_v2) collected for this study. FAGE\_v2 was curated via Internet image searches
                of 500 individuals evenly distributed across 10 African countries. VGGFace was trained on FAGE\_v2
                to obtain the best accuracy of 81.80\%.
        output: VGGFace
        input: The current paper presents an improved model, called sparse HMAX, which integrates sparse firing.
                This model is able to learn higher-level features of objects on unlabeled training images. Unlike
                most other deep learning models that explicitly address global structure of images in every layer,
                sparse HMAX addresses local to global structure gradually along the hierarchy by applying patch-based
                learning to the output of the previous layer.
        output: sparse HMAX
        input: Furthermore, to integrate action-sensitive information into VLM, we introduce Action-Cue-Injected
                Temporal Prompt Learning (ActPrompt), which injects action cues into the image encoder of VLM for
                better discovering action-sensitive patterns.
        output: ActPrompt
        input: Multimodal Large Language Models (MLLMs) demonstrate remarkable image-language capabilities, but
                their widespread use faces challenges in cost-effective training and adaptation. Existing
                approaches often necessitate expensive language model retraining and limited adaptability.
                Additionally, the current focus on zero-shot performance improvements offers insufficient guidance
                for task-specific tuning.
        output: 😞
        input: Most vulnerability detection studies focus on datasets of vulnerabilities in C/C++ code, offering
                limited language diversity. Thus, the effectiveness of deep learning methods, including large language
                models (LLMs), in detecting software vulnerabilities beyond these languages is still largely unexplored.
        output: 😞
        """  # noqa: E501, W605
            ),
            HumanMessage(content=f"""{abstract}"""),
        ]

        parser: StrOutputParser = StrOutputParser()
        # parser = JsonOutputParser()

        chain = model | parser
        resp: str = chain.invoke(input=promptTemplate)

        results.append({"doi": doi, "prompt": abstract, "response": resp})

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
