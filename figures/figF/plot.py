from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas
import seaborn as sns
from pandas import DataFrame


def load_parquet(fp: Path) -> DataFrame:
    # Read file contents from Apache Parquet file
    return pandas.read_parquet(path=fp, engine="pyarrow")


def preprocess_data(df: DataFrame) -> DataFrame:
    df = df.drop(
        columns=[
            "raw_jats_xml",
            "formatted_jats_xml",
            "raw_markdown",
            "formatted_markdown",
            "dois",
        ]
    )

    df = df.rename(
        columns={
            "raw_jats_xml_tokens": "JATS XML",
            "formatted_jats_xml_tokens": "Formatted JATS XML",
            "raw_markdown_tokens": "Markdown",
            "formatted_markdown_tokens": "Formatted Markdown",
        }
    )

    df = df[sorted(df.columns, key=lambda col: df[col].max(), reverse=True)]
    return df


def plot(df: DataFrame) -> None:
    sns.boxplot(data=df, showfliers=False)
    plt.suptitle("Size Of Document Types By Token Count")
    plt.title(label="Tokens computed with `tiktoken/gpt-4`")
    plt.xlabel(xlabel="Document Format")
    plt.ylabel(ylabel="Token Count")

    plt.tight_layout()
    plt.savefig("figF.pdf")


@click.command()
@click.option(
    "-i",
    "--input-fp",
    help="Path to dataset file created scripts/2-create-llm-analysis-datasets",
    type=lambda x: Path(x).resolve(),
    required=True,
)
def main(input_fp: Path) -> None:
    df: DataFrame = load_parquet(fp=input_fp)

    df = preprocess_data(df=df)

    plot(df=df)


if __name__ == "__main__":
    main()
