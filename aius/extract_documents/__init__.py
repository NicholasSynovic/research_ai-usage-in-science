from json import loads

import pandas
from bs4 import BeautifulSoup, ResultSet, Tag
from pandas import DataFrame, Series
from pandas.core.groupby import DataFrameGroupBy
from progress.bar import Bar


class JournalExtractor:
    def __init__(self, search_data: DataFrame) -> None:
        self.search_data: DataFrame = search_data

        self.datum_template: dict[str, list] = {"search_id": [], "doi": []}

    def _extract_plos(self, row: Series) -> DataFrame:
        # Copy template
        datum: dict[str, list] = self.datum_template.copy()

        # Get JSON object
        json_str: str = row["html"]
        json_dict: dict = loads(s=json_str)

        # Parse JSON for DOIs
        docs: list[dict] = json_dict["searchResults"]["docs"]
        doc: dict
        for doc in docs:
            datum["search_id"].append(row["_id"])
            datum["doi"].append(f"https://doi.org/{doc['id']}")

        return DataFrame(data=datum)

    def _extract_nature(self, row: Series) -> DataFrame:
        # Copy template
        datum: dict[str, list] = self.datum_template.copy()

        # Get BeautifulSoup object
        soup: BeautifulSoup = BeautifulSoup(markup=row["html"], features="lxml")

        # Parser BeautifulSoup for DOIs
        links: ResultSet[Tag] = soup.find_all(
            name="a",
            attrs={
                "class": "c-card__link",
            },
        )

        link: Tag
        for link in links:
            suffix: str = link.get(key="href").split("/")[-1]

            datum["search_id"].append(row["_id"])
            datum["doi"].append(f"https://doi.org/10.1038/{suffix}")

        return DataFrame(data=datum)

    def _create_search_paper_relationships(
        self, papers_df: DataFrame, unique_papers_df: DataFrame
    ) -> DataFrame:
        # Create storage variable
        data: dict[str, list] = {
            "search_id": [],
            "paper_id": [],
        }

        # Group by paper DOI
        paper_groups: DataFrameGroupBy = papers_df.groupby(by="doi")

        with Bar(
            "Creating journal search and paper relationships...",
            max=unique_papers_df.shape[0],
        ) as bar:
            # Iterate through each group
            doi: str
            paper_group: DataFrame
            for doi, paper_group in paper_groups:
                # Get the paper ID from the unique papers DataFrame
                paper_id: int = unique_papers_df.loc[
                    unique_papers_df["doi"] == doi
                ].index[0]

                # Add `paper_id` as a column to `paper_group`
                paper_group["paper_id"] = paper_id

                # Extend datum object with columns
                data["search_id"].extend(paper_group["search_id"])
                data["paper_id"].extend(paper_group["paper_id"])

                # Increment spinner
                bar.next()

        return DataFrame(data=data)

    def extract_all_papers(self) -> DataFrame:
        df_list: list[DataFrame] = []

        with Bar(
            "Extracting papers from search results...", max=self.search_data.shape[0]
        ) as bar:
            row: Series
            for _, row in self.search_data.iterrows():
                match row["journal"]:
                    case "plos":
                        df_list.append(self._extract_plos(row=row))
                    case "nature":
                        df_list.append(self._extract_nature(row=row))
                bar.next()

        data: DataFrame = pandas.concat(objs=df_list, ignore_index=True)
        return data.drop_duplicates(ignore_index=True)

    def organize_papers(self, papers_df: DataFrame) -> tuple[DataFrame, DataFrame]:
        # Get the unique set of paper DOIs
        unique_papers_df: DataFrame = papers_df.drop_duplicates(
            subset=["doi"],
            ignore_index=True,
        )
        unique_papers_df = unique_papers_df.drop(columns="search_id")

        # Create relationships
        search_paper_relationship: DataFrame = self._create_search_paper_relationships(
            papers_df=papers_df,
            unique_papers_df=unique_papers_df,
        )

        return (unique_papers_df, search_paper_relationship)
