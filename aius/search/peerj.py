from itertools import product
from logging import Logger
from string import Template

from progress.bar import Bar
from requests import Session
from requests.adapters import HTTPAdapter, Retry

from aius.db import DB
from aius.search.megajournal import ArticleModel, MegaJournal, SearchModel


class PeerJ(MegaJournal):
    def __init__(self, logger: Logger, db: DB) -> None:
        self.logger: Logger = logger

        # Load default variable values
        super().__init__()

        # Set constants
        self.db = db
        self.megajournal: str = "PeerJ"
        self.search_url_template: Template = Template(
            template="https://peerj.com/search-get/v2/?q=${search_keyword}&type=articles&published-gte=${year}&published-lte=${year}&page=${page}"
        )

        self.keyword_year_products: product = product(
            self.db.get_search_keywords(),
            self.db.get_years(),
        )

        # Custom HTTPS session with exponential backoff enabled
        self.session: Session = Session()
        self.session.mount(
            "https://",
            HTTPAdapter(
                max_retries=Retry(
                    total=10,
                    backoff_factor=2,
                    respect_retry_after_header=False,
                    status_forcelist=[429, 500, 502, 503, 504],
                ),
            ),
        )

        self.logger.info(msg=f"Mega Journal: {self.megajournal}")
        self.logger.info(msg=f"Keyword-Year products: {self.keyword_year_products}")

    def _compute_total_number_of_pages(self, resp: SearchModel) -> int:
        return resp.json_data["pages"]

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
                docs: list[dict] = response.json_data["results"]

                doc: dict
                for doc in docs:
                    doc_data: dict = doc["data"]

                    data.append(
                        ArticleModel(
                            doi=f"https://doi.org/{doc_data['doi']}",
                            title=doc_data["title"],
                            megajournal=self.megajournal,
                            journal=doc["journalSlug"],
                            search_id=response_index,
                        )
                    )

                response_index += 1
                bar.next()

        return data
