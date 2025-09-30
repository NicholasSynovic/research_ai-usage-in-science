from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from pandas import DataFrame


def load_parquet(fp: Path) -> DataFrame:
    # Read file contents from Apache Parquet file
    return pandas.read_parquet(path=fp, engine="pyarrow")


@click.command()
@click.option(
    "-1",
    "--formatted-jats-path",
    help="Path to formatted JATS token count Apache Parquet file",
    type=lambda x: Path(x).resolve(),
)
@click.option(
    "-2",
    "--formatted-md-path",
    help="Path to formatted MD token count Apache Parquet file",
    type=lambda x: Path(x).resolve(),
)
@click.option(
    "-3",
    "--unformatted-jats-path",
    help="Path to unformatted JATS token count Apache Parquet file",
    type=lambda x: Path(x).resolve(),
)
@click.option(
    "-4",
    "--unformatted-MD-path",
    help="Path to unformatted MD token count Apache Parquet file",
    type=lambda x: Path(x).resolve(),
)
@click.option(
    "-o",
    "--output",
    help="Path to write figure to",
    type=lambda x: Path(x).resolve(),
)
def main(
    formatted_jats_path: Path,
    unformatted_jats_path: Path,
    formatted_md_path: Path,
    unformatted_md_path: Path,
    output: Path,
) -> None:
    df1: DataFrame = load_parquet(fp=formatted_jats_path)
    df2: DataFrame = load_parquet(fp=unformatted_jats_path)
    df3: DataFrame = load_parquet(fp=formatted_md_path)
    df4: DataFrame = load_parquet(fp=unformatted_md_path)

    df1["type"] = "Formatted JATS XML"
    df2["type"] = "JATS XML"
    df3["type"] = "Formatted Markdown"
    df4["type"] = "Markdown"

    data: DataFrame = pandas.concat(
        objs=[
            df1[["type", "tokens"]],
            df2[["type", "tokens"]],
            df3[["type", "tokens"]],
            df4[["type", "tokens"]],
        ],
        ignore_index=True,
    )

    sns.boxplot(data=data, x="type", y="tokens", showfliers=False)
    plt.suptitle("Size Of Document Types By Token Count")
    plt.title(label="Tokens computed with `tiktoken/gpt-4`")
    plt.xlabel(xlabel="Document Format")
    plt.ylabel(ylabel="Token Count")

    plt.tight_layout()
    plt.savefig(output)


if __name__ == "__main__":
    main()
