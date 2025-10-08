from pathlib import Path
from zipfile import ZipFile

import click
import pandas
import tiktoken
from bs4 import BeautifulSoup
from bs4.element import Tag
from pandas import DataFrame
from progress.bar import Bar
from tiktoken.core import Encoding

from aius.db import DB

# Query to get all natural science papers
SQL_QUERY: str = """
SELECT a.*
FROM papers a
JOIN ns_papers b ON a._id = b.paper_id;
"""


def read_file_from_archive(filename: str, archive: ZipFile) -> BeautifulSoup:
    # Read file contents from zipfile
    return BeautifulSoup(
        markup=archive.open(name=filename, mode="r"),
        features="lxml-xml",
    )


def count_tokens(text: str, encoding: Encoding) -> int:
    return len(encoding.encode(text=text))


@click.command()
@click.option(
    "-i",
    "--input-path",
    help="Path to all PLOS documents in JATS XML format in a single zip file",
    type=lambda x: Path(x).resolve(),
)
@click.option(
    "-d",
    "--db-path",
    help="Path to AIUS SQLite3 database file",
    type=lambda x: Path(x).resolve(),
)
@click.option(
    "-o",
    "--output-path",
    help="Path to write output Apache Parquet file",
    type=lambda x: Path(x).resolve(),
)
def main(input_path: Path, db_path: Path, output_path: Path) -> None:
    # Data structure to hold content information
    data: dict[str, list] = {"filename": [], "tokens": [], "content": []}

    # Connect to the database
    db: DB = DB(db_path=db_path)

    # Instantiate encoding
    encoding: Encoding = tiktoken.encoding_for_model("gpt-4")

    # Read data from the database into a DataFrame
    df: DataFrame = pandas.read_sql_query(sql=SQL_QUERY, con=db.engine)

    # Get only PLOS documents
    df = df[df["doi"].str.contains(pat="doi.org/10.1371")]

    # Drop DOI URL frontmatter
    df["filename"] = (
        df["doi"].str.replace(pat="https://doi.org/10.1371/", repl="") + ".xml"
    )

    # Extract text, compute token size, and store data
    with Bar("Computing tokens...", max=df["filename"].size) as bar:
        with ZipFile(input_path, "r") as archive:
            filename: str
            for filename in df["filename"]:
                soup: BeautifulSoup = read_file_from_archive(
                    filename=filename,
                    archive=archive,
                )
                xml_string: str = soup.prettify()
                token_count: int = count_tokens(
                    text=xml_string,
                    encoding=encoding,
                )

                data["filename"].append(filename)
                data["content"].append(xml_string)
                data["tokens"].append(token_count)

                bar.next()

            archive.close()

    output_df: DataFrame = DataFrame(data=data)
    output_df.to_parquet(path=output_path, engine="pyarrow")


if __name__ == "__main__":
    main()
