from pathlib import Path

import click
import mdformat
import pandas
import tiktoken
from pandas import DataFrame, Series
from progress.bar import Bar
from requests import Response, post
from tiktoken.core import Encoding


def load_parquet(fp: Path) -> DataFrame:
    # Read file contents from Apache Parquet file
    return pandas.read_parquet(path=fp, engine="pyarrow")


def convert_jats_to_md(text: str, pandoc_api: str) -> str:
    resp: Response = post(
        url=pandoc_api,
        json={
            "text": text,
            "from": "jats",
            "to": "markdown",
        },
    )

    return mdformat.text(md=resp.content.decode())


def count_tokens(text: str, encoding: Encoding) -> int:
    return len(encoding.encode(text=text))


@click.command()
@click.option(
    "-i",
    "--input-path",
    help="Path to formatted JATS token count Apache Parquet file",
    type=lambda x: Path(x).resolve(),
)
@click.option(
    "-p",
    "--pandoc-api",
    help="Pandoc web server API URL",
    type=str,
    default="http://localhost:3030",
    show_default=True,
)
@click.option(
    "-o",
    "--output-path",
    help="Path to write output Apache Parquet file",
    type=lambda x: Path(x).resolve(),
)
def main(input_path: Path, pandoc_api: str, output_path: Path) -> None:
    # Data structure to hold content information
    data: dict[str, list] = {"filename": [], "tokens": [], "content": []}

    # Instantiate encoding
    encoding: Encoding = tiktoken.encoding_for_model("gpt-4")

    # Read data from the database into a DataFrame
    df: DataFrame = load_parquet(fp=input_path)
    df = df[["filename", "content"]]

    # Extract text, compute token size, and store data
    with Bar(
        "Converting to Markdown and computing tokens...",
        max=df["filename"].size,
    ) as bar:
        row: Series
        for _, row in df.iterrows():
            markdown: str = convert_jats_to_md(
                text=row["content"],
                pandoc_api=pandoc_api,
            )

            token_count: int = count_tokens(
                text=markdown,
                encoding=encoding,
            )

            data["filename"].append(row["filename"])
            data["content"].append(markdown)
            data["tokens"].append(token_count)

            bar.next()

    output_df: DataFrame = DataFrame(data=data)
    output_df.to_parquet(path=output_path, engine="pyarrow")


if __name__ == "__main__":
    main()
