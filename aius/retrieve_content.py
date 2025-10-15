from pathlib import Path
from typing import Literal
from zipfile import ZipFile

import pandas as pd
from bs4 import BeautifulSoup, ResultSet, Tag
from progress.bar import Bar
from tiktoken import Encoding, encoding_for_model

from aius.db import DB
from aius.pandoc import PandocAPI


class RetrieveContent:
    def __init__(
        self,
        db: DB,
        archive_path: Path,
        pandoc_api: PandocAPI,
    ) -> None:
        # Global variables
        self.archive_path: Path = archive_path.resolve()
        self.pandoc_api: PandocAPI = pandoc_api

        # SQLite3 query Get natural science PLOS DOIs
        sql_query: str = """
        SELECT ppd.* FROM plos_paper_dois ppd
        JOIN plos_natural_science_papers pnsp
        ON pnsp.plos_paper_id = ppd._id;
        """

        # Execute SQLite3 query
        self.dois: pd.DataFrame = pd.read_sql_query(
            sql=sql_query,
            con=db.engine,
        )

        # Get size of DataFrame
        self.doi_count: int = self.dois.shape[0]

        # Format DOIs to fit zip archive filenames
        self.dois["filename"] = self.dois["doi"].apply(
            lambda x: x.replace("https://doi.org/10.1371/", "") + ".xml",
        )

        # Run retrieval
        self.content_df: pd.DataFrame = self.extract_content()
        self.format_jats()  # Operates on self.content_df directly
        self.convert_jats(column_name="raw_md")
        self.convert_jats(column_name="formatted_md")
        self.compute_tokens()

    def extract_content(self) -> pd.DataFrame:
        # Data structure to store content
        data: dict[str, list[str | int]] = {
            "plos_paper_id": [],
            "raw_jats_xml": [],
        }

        with Bar(
            "Extracting JATS XML content from PLOS zip archive...",
            max=self.doi_count,
        ) as bar:
            with ZipFile(file=self.archive_path, mode="r") as zf:
                # For each filename, open the file's content and add it to the
                # data structure
                row: pd.Series
                for _, row in self.dois.iterrows():
                    # Open the file and decode the content
                    with zf.open(name=row["filename"], mode="r") as fp:
                        data["plos_paper_id"].append(row["_id"])

                        # Add prettified JATS XML to the data structure
                        data["raw_jats_xml"].append(
                            BeautifulSoup(
                                markup=fp.read().decode().strip("\n"),
                                features="lxml-xml",
                            ).prettify()
                        )

                        fp.close()
                    bar.next()
                zf.close()

        return pd.DataFrame(data=data)

    def format_jats(self) -> None:
        # Store data to be appended to DataFrame
        data: list[str] = []

        with Bar(
            "Formatting JATS XML content to remove extra content...",
            max=self.doi_count,
        ) as bar:
            row: pd.Series
            for _, row in self.content_df.iterrows():
                # Create soup from text
                soup: BeautifulSoup = BeautifulSoup(
                    markup=row["raw_jats_xml"],
                    features="lxml-xml",
                )

                # Remove frontmatter
                front_tag: Tag = soup.find(name="front")
                front_tag.decompose()

                # Remove citations
                back_tag: Tag = soup.find(name="back")
                back_tag.decompose()

                # Remove citations in the prose
                citation_tags: ResultSet[Tag] = soup.find_all(name="xref")
                citation_tag: Tag
                for citation_tag in citation_tags:
                    citation_tag.decompose()

                # Remove figures in the prose
                figure_tags: ResultSet[Tag] = soup.find_all(name="fig")
                figure_tag: Tag
                for figure_tag in figure_tags:
                    figure_tag.decompose()

                # Remove inline formulas in the prose
                figure_tags: ResultSet[Tag] = soup.find_all(name="inline-formula")
                figure_tag: Tag
                for figure_tag in figure_tags:
                    figure_tag.decompose()

                # Remove display formulas in the prose
                figure_tags: ResultSet[Tag] = soup.find_all(name="disp-formula")
                figure_tag: Tag
                for figure_tag in figure_tags:
                    figure_tag.decompose()

                # Remove display formulas in the prose
                figure_tags: ResultSet[Tag] = soup.find_all(name="disp-quote")
                figure_tag: Tag
                for figure_tag in figure_tags:
                    figure_tag.decompose()

                # Append prettified content to list
                data.append(soup.prettify())
                bar.next()

        self.content_df["formatted_jats_xml"] = data

    def convert_jats(self, column_name: Literal["raw_md", "formatted_md"]) -> None:
        # Data structure to store content
        data: list[str] = []

        with Bar(max=self.doi_count) as bar:
            jats_xml_series: pd.Series

            # Match on column name
            match column_name:
                case "raw_md":
                    bar.message = "Converting raw JATS XML to MD..."
                    jats_xml_series = self.content_df["raw_jats_xml"]
                case "formatted_md":
                    bar.message = "Converting formatted JATS XML to MD..."
                    jats_xml_series = self.content_df["formatted_jats_xml"]

            jats_xml: str
            for jats_xml in jats_xml_series:
                data.append(
                    self.pandoc_api.convert_jats_to_md(
                        jats_xml=jats_xml,
                    )
                )
                bar.next()

        self.content_df[column_name] = data

    def compute_tokens(self) -> None:
        encoding: Encoding = encoding_for_model(model_name="gpt-4")

        print("Computing token count for raw JATS XML...")
        self.content_df["raw_jats_xml_token_count"] = self.content_df[
            "raw_jats_xml"
        ].apply(lambda x: len(encoding.encode(text=x)))

        print("Computing token count for formatted JATS XML...")
        self.content_df["formatted_jats_xml_token_count"] = self.content_df[
            "formatted_jats_xml"
        ].apply(lambda x: len(encoding.encode(text=x)))

        print("Computing token count for raw MD...")
        self.content_df["raw_md_token_count"] = self.content_df["raw_md"].apply(
            lambda x: len(encoding.encode(text=x))
        )

        print("Computing token count for formatted MD...")
        self.content_df["formatted_md_token_count"] = self.content_df[
            "formatted_md"
        ].apply(lambda x: len(encoding.encode(text=x)))
