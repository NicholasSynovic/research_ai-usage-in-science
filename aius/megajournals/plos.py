from itertools import product
from logging import Logger
from math import ceil
from string import Template
from zipfile import ZipFile

from bs4 import BeautifulSoup
from pandas import DataFrame, Series
from progress.bar import Bar

from aius.db import DB
from aius.megajournals import ArticleModel, MegaJournal, SearchModel


class PLOS(MegaJournal):
    def __init__(self, logger: Logger, db: DB) -> None:
        # Load default variable values
        super().__init__(logger=logger, db=db)

        self.megajournal: str = "PLOS"
        self.search_url_template: Template = Template(
            template="https://journals.plos.org/plosone/dynamicSearch?filterArticleTypes=Research Article&sortOrder=DATE_NEWEST_FIRST&resultsPerPage=100&q=${search_keyword}&filterStartDate=${year}-01-01&filterEndDate=${year}-12-31&page=${page}"
        )

        self.keyword_year_products: product = product(
            self.db.get_search_keywords(),
            self.db.get_years(),
        )

        self.logger.info(msg=f"Mega Journal: {self.megajournal}")
        self.logger.info(msg=f"Keyword-Year products: {self.keyword_year_products}")

    def _compute_total_number_of_pages(self, resp: SearchModel) -> int:
        documents_found: int = int(resp.json_data["searchResults"]["numFound"])
        self.logger.info(msg=f"Total number of documents found: {documents_found}")

        pages: int = ceil(documents_found / 100)
        self.logger.info(msg=f"Total number of pages to search through: {pages}")

        return pages

    def search(self) -> list[SearchModel]:
        data: list[SearchModel] = []

        pair: tuple[str, int]
        for pair in self.keyword_year_products:
            self.logger.debug(msg=f"Keyword year pair being searched for: {pair}")

            with Bar(
                f"Searching {self.megajournal} for {pair[0]} in {pair[1]}...",
                max=1,
            ) as bar:
                # Get the first page of results
                resp: SearchModel = self.search_single_page(
                    logger=self.logger,
                    keyword_year_pair=pair,
                    page=1,
                )
                data.append(resp)
                bar.next()

                # Get the number of pages to iterate through
                page_count = self._compute_total_number_of_pages(resp=resp)

                # Iterate to the next page if page_count == 1
                if page_count <= 1:
                    continue
                else:
                    bar.max = page_count
                    bar.update()

                page: int
                for page in range(2, page_count + 1):
                    resp: SearchModel = self.search_single_page(
                        logger=self.logger,
                        keyword_year_pair=pair,
                        page=page,
                    )
                    data.append(resp)
                    bar.next()

        return data

    def parse_response(self, responses: list[SearchModel]) -> list[ArticleModel]:
        data: list[ArticleModel] = []

        response_index: int = 0

        with Bar(
            "Extracting articles from search results...", max=len(responses)
        ) as bar:
            response: SearchModel
            for response in responses:
                docs: list[dict] = response.json_data["searchResults"]["docs"]

                doc: dict
                for doc in docs:
                    data.append(
                        ArticleModel(
                            doi=doc["id"],
                            title=doc["title"],
                            megajournal=self.megajournal,
                            journal=doc["journal_name"],
                            search_id=response_index,
                        )
                    )

                response_index += 1
                bar.next()

        return data

    def download_jats(self, df: DataFrame, **kwargs) -> DataFrame:
        data: dict[str, list[str | int]] = {
            "doi": [],
            "jats_xml": [],
        }

        with (
            Bar(
                "Extracting JATS XML content from PLOS zip archive...",
                max=df.shape[0],
            ) as bar,
            ZipFile(file=plos_zip_fp, mode="r") as zf,
        ):
            # For each filename, open the file's content and add it to the
            # data structure
            row: Series
            for _, row in df.iterrows():
                # Open the file and decode the content
                filename: str = row["doi"].split("/")[1] + ".xml"
                with zf.open(name=filename, mode="r") as fp:
                    data["doi"].append(row["doi"])

                    # Add prettified JATS XML to the data structure
                    data["jats_xml"].append(
                        BeautifulSoup(
                            markup=fp.read().decode("UTF-8").strip("\n"),
                            features="lxml",
                        ).prettify()
                    )

                    fp.close()
                bar.next()
            zf.close()

        return DataFrame(data=data)
