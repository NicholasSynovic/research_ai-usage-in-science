from json import loads

import pandas
from pandas import DataFrame, Series
from progress.bar import Bar
from bs4 import BeautifulSoup, ResultSet, Tag


class JournalExtractor:
    def __init__(self, search_data: DataFrame) -> None:
        self.search_data: DataFrame = search_data

        self.datum_template: dict[str, list] = {"search_id": [], "doi": []}

    def _extract_plos(self, idx, row: Series) -> DataFrame:
        # Copy template
        datum: dict[str, list] = self.datum_template.copy()

        # Get JSON object
        json_str: str = row["html"]
        json_dict: dict = loads(s=json_str)

        # Parse JSON for DOIs
        docs: list[dict] = json_dict["searchResults"]["docs"]
        doc: dict
        for doc in docs:
            datum["search_id"].append(idx)
            datum["doi"].append(f"https://doi.org/{doc['id']}")

        return DataFrame(data=datum)

    def _extract_nature(self, idx, row: Series) ->  DataFrame:
         # Copy template
        datum: dict[str, list] = self.datum_template.copy()

        # Get BeautifulSoup object
        soup: BeautifulSoup = BeautifulSoup(markup=row["html"], features="lxml")

        # Parser BeautifulSoup for DOIs
        links: ResultSet[Tag] = soup.find_all(name="a", attrs={"class": "c-card__link",})

        link: Tag
        for link in links:
            suffix: str = link.get(key="href").split("/")[-1]

            datum["search_id"].append(idx)
            datum["doi"].append(f"https://doi.org/10.1038/{suffix}")

        return DataFrame(data=datum)

    def extract_all_papers(self) -> DataFrame:
        df_list: list[DataFrame] = []

        with Bar(
            "Extracting papers from search results...", max=self.search_data.shape[0]
        ) as bar:
            row: Series
            for idx, row in self.search_data.iterrows():
                match row["journal"]:
                    case "plos":
                        df_list.append(self._extract_plos(idx=idx, row=row))
                    case "nature":
                        df_list.append(self._extract_nature(idx=idx, row=row))
                bar.next()

        return pandas.concat(objs=df_list, ignore_index=True)
