from pathlib import Path
from zipfile import ZipFile

import click
from bs4 import BeautifulSoup, Tag
from dois import *
from mdformat import text
from pandas import DataFrame
from progress.bar import Bar
from requests import Response, post
from tiktoken import Encoding, encoding_for_model


def load_dois(ds: str) -> list[str]:
    data: list[str] = []

    match ds:
        case "small":
            data = SMALL_SAMPLE
        case "manual-review":
            data = MANUAL_REVIEWED_POPULTION

    return data


def read_zipfile(fp: Path, dois: list[str]) -> dict[str, BeautifulSoup]:
    data: dict[str, BeautifulSoup] = {}

    with Bar("Reading content from zip file...", max=len(dois)) as bar:
        # zf = Zip file
        with ZipFile(file=fp, mode="r") as zf:
            doi: str
            for doi in dois:
                # cf = Compressed file
                with zf.open(name=doi, mode="r") as cf:
                    content: str = cf.read().decode(encoding="utf-8")
                    data[doi] = BeautifulSoup(
                        markup=content,
                        features="lxml-xml",
                    )
                    cf.close()

                bar.next()

            zf.close()

    return data


def handle_raw_jats_xml(soups: list[BeautifulSoup]) -> list[str]:
    data: list[str] = []

    soup_copies: list[BeautifulSoup] = soups.copy()

    with Bar("Handling raw JATS XML content...", max=len(soup_copies)) as bar:
        soup: BeautifulSoup
        for soup in soup_copies:
            data.append(soup.prettify())
            bar.next()

    return data


def handle_formatted_jats_xml(soups: list[BeautifulSoup]) -> list[str]:
    data: list[str] = []

    soup_copies: list[BeautifulSoup] = soups.copy()

    with Bar("Handling formatted JATS XML content...", max=len(soup_copies)) as bar:
        soup: BeautifulSoup
        for soup in soup_copies:
            front_tag: Tag = soup.find(name="front")
            front_tag.decompose()

            back_tag: Tag = soup.find(name="back")
            back_tag.decompose()

            data.append(soup.prettify())
            bar.next()

    return data


def convert_jats_to_xml(
    content_list: list[str],
    pandoc_uri: str = "localhost:3030",
) -> list[str]:
    data: list[str] = []

    json_body: dict[str, str] = {"from": "jats", "to": "markdown"}

    with Bar(
        "Converting JATS XML content to Markdown...",
        max=len(content_list),
    ) as bar:
        content: str
        for content in content_list:
            json_body["text"] = content

            resp: Response = post(
                url=f"http://{pandoc_uri}",
                json=json_body,
                timeout=60,
            )
            md: str = text(md=resp.content.decode(encoding="utf-8"))

            data.append(md)

            bar.next()

    return data


def encode_documents(encoding: Encoding, documents: list[str]) -> list[int]:
    data: list[int] = []

    with Bar("Encoding documents...", max=len(documents)) as bar:
        document: str
        for document in documents:
            data.append(len(encoding.encode(text=document)))
            bar.next()

    return data


@click.command()
@click.option(
    "-i",
    "--input-fp",
    required=True,
    type=lambda x: Path(x).resolve(),
    help="Path to PLOS JATS XML archive",
)
@click.option(
    "-d",
    "--dataset-size",
    default="small",
    required=False,
    show_default=True,
    help="Dataset size",
    type=click.Choice(choices=["small", "manual-review"]),
)
@click.option(
    "-o",
    "--output-fp",
    default=Path("prompt_testing_dataset.parquet"),
    required=False,
    show_default=True,
    help="Path to store dataset as an Apache Parquet File",
    type=lambda x: Path(x).resolve(),
)
def main(
    input_fp: Path,
    output_fp: Path,
    dataset_size: str = "small",
) -> None:
    # Load DOIs to parse for
    dois: list[str] = load_dois(ds=dataset_size)

    # Get DOI content from zip archive
    doi_content_mapping: dict[str, BeautifulSoup] = read_zipfile(
        fp=input_fp,
        dois=dois,
    )
    dois: list[str] = list(doi_content_mapping.keys())
    soups: list[BeautifulSoup] = list(doi_content_mapping.values())

    # Handle different content types
    raw_jats_xml: list[str] = handle_raw_jats_xml(soups=soups)
    formatted_jats_xml: list[str] = handle_formatted_jats_xml(soups=soups)
    raw_markdown: list[str] = convert_jats_to_xml(content_list=raw_jats_xml)
    formatted_markdown: list[str] = convert_jats_to_xml(
        content_list=formatted_jats_xml,
    )

    # Encode documents
    encoding: Encoding = encoding_for_model(model_name="gpt-4")
    raw_jats_tokens: list[int] = encode_documents(
        encoding=encoding,
        documents=raw_jats_xml,
    )
    formatted_jats_tokens: list[int] = encode_documents(
        encoding=encoding,
        documents=formatted_jats_xml,
    )
    raw_markdown_tokens: list[int] = encode_documents(
        encoding=encoding,
        documents=raw_markdown,
    )
    formatted_markdown_tokens: list[int] = encode_documents(
        encoding=encoding,
        documents=formatted_markdown,
    )

    # Write data to file
    data: dict[str, list[str | int]] = {
        "dois": dois,
        "raw_jats_xml": raw_jats_xml,
        "formatted_jats_xml": formatted_jats_xml,
        "raw_markdown": raw_markdown,
        "formatted_markdown": formatted_markdown,
        "raw_jats_xml_tokens": raw_jats_tokens,
        "formatted_jats_xml_tokens": formatted_jats_tokens,
        "raw_markdown_tokens": raw_markdown_tokens,
        "formatted_markdown_tokens": formatted_markdown_tokens,
    }
    df: DataFrame = DataFrame(data=data)
    df.to_parquet(path=output_fp)

    # Print max token size stats
    print("Raw JATS XML Max Tokens:", df["raw_jats_xml_tokens"].max())
    print("Formatted JATS XML Max Tokens:", df["formatted_jats_xml_tokens"].max())
    print("Raw Markdown Max Tokens:", df["raw_markdown_tokens"].max())
    print("Formatted Markdown Max Tokens:", df["formatted_markdown_tokens"].max())


if __name__ == "__main__":
    main()
