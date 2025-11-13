from itertools import product
from logging import Logger
from math import ceil
from string import Template

from progress.bar import Bar

from aius.db import DB
from aius.search.megajournal import ArticleModel, MegaJournal, SearchModel


class PLOS(MegaJournal):
    def __init__(self, logger: Logger, db: DB) -> None:
        self.logger: Logger = logger

        # Load default variable values
        super().__init__()

        # Set constants
        self.db = db
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
                if page_count == 1:
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
        return []
