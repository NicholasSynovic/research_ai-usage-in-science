from pathlib import Path
from zipfile import ZipFile

import pandas as pd
from bs4 import BeautifulSoup, Tag
from progress.bar import Bar

from aius.db import DB


class RetrieveContent:
    def __init__(self, db: DB, archive_path: Path) -> None:
        # Global variables
        self.archive_path: Path = archive_path.resolve()

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
                                markup=fp.read().decode(), features="lxml-xml"
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

                # Append prettified content to list
                data.append(soup.prettify())
                bar.next()

        self.content_df["formatted_jats_xml"] = data
