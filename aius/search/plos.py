from itertools import product
from logging import Logger
from string import Template

from progress.bar import Bar

from aius.db import DB
from aius.search.megajournal import ArticleModel, MegaJournal, ResponseModel


class PLOS(MegaJournal):
    def __init__(self, logger: Logger, db: DB) -> None:
        super().__init__()
        self.megajournal: str = "PLOS"
        self.search_url_template: Template = Template(
            template="https://journals.plos.org/plosone/dynamicSearch?filterArticleTypes=Research Article&q=${search_keyword}&sortOrder=DATE_NEWEST_FIRST&page=${page}"
        )

        self.keyword_year_products: product = product(
            db.get_search_keywords(),
            db.get_years(),
        )

        logger.info(msg=f"Mega Journal: {self.megajournal}")
        logger.info(msg=f"Keyword-Year products: {list(self.keyword_year_products)}")

    def search(self) -> list[ResponseModel]:
        return []

    def parse_response(self, responses: list[ResponseModel]) -> list[ArticleModel]:
        return []
