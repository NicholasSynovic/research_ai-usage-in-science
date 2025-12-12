from datetime import datetime, timezone
from itertools import product
from json import dumps, loads
from logging import Logger

from pandas import DataFrame, Series
from progress.bar import Bar
from requests import HTTPError, Response

from aius.db import DB
from aius.megajournals.megajournal import MegaJournal
from aius.megajournals.models import ArticleModel, SearchModel


class FrontiersIn(MegaJournal):
    def __init__(self, logger: Logger, db: DB) -> None:
        # Load default variable values
        super().__init__(logger=logger, db=db)

        # Set constants
        self.megajournal: str = "FrontiersIn"
        self.search_api_endpoint: str = "https://www.frontiersin.org/api/v2/search"
        self.search_api_body: dict = {
            "Filter": {
                "ArticleType": 0,
                "Date": 0,
                "DomainId": 0,
                "JournalId": 0,
                "PartOfResearchTopic": 0,
                "SectionId": 0,
                "Sort": 1,
            },
            "Search": "",  # Change this to search for a keyword
            "SearchType": 2,
            "Skip": 0,
            "Top": 1,  # Change this to get more search results
            "UserId": 0,
        }

        self.keyword_year_products: product = product(
            self.db.get_search_keywords(),
            self.db.get_years(),
        )

        self.logger.info(msg=f"Mega Journal: {self.megajournal}")
        self.logger.info(msg=f"Keyword-Year products: {self.keyword_year_products}")

    def _compute_total_number_of_papers(self, resp: SearchModel) -> int:
        documents_found: int = int(resp.json_data["Summary"]["Article"]["Count"])
        self.logger.info(msg=f"Total number of documents found: {documents_found}")

        return documents_found

    def search_single_page(
        self,
        logger: Logger,
        keyword_year_pair: tuple[str, int],
        page: int = 1,
    ) -> SearchModel:
        # NOTE: Page is used to update the number of documents being searched for
        # Update the search request body
        search_request_body: dict = self.search_api_body.copy()
        search_request_body["Search"] = keyword_year_pair[0]
        search_request_body["Top"] = page
        logger.info(msg=f"Search API JSON data: {dumps(obj=search_request_body)}")

        timestamp: float = datetime.now(tz=timezone.utc).timestamp()
        resp: Response = self.session.post(
            url=self.search_api_endpoint,
            json=search_request_body,
            timeout=self.timeout,
        )
        logger.debug(msg=f"Response status code: {resp.status_code}")

        if resp.status_code != 200:
            logger.error(msg=f"Non 200 response code: {resp.content}")

        return SearchModel(
            timestamp=timestamp,
            megajournal=self.megajournal,
            search_keyword=keyword_year_pair[0],
            status_code=resp.status_code,
            year=keyword_year_pair[1],
            page=page,
            url=f"{self.search_api_endpoint} + {dumps(obj=search_request_body)}",
            json_data=resp.json(),
        )

    def search(self) -> list[SearchModel]:
        data: list[SearchModel] = []

        keywords: list[str] = sorted(
            list({pair[0] for pair in self.keyword_year_products})
        )

        keyword: str
        for keyword in keywords:
            self.logger.debug(msg=f"Keyword being searched for: {keyword}")

            print(f"Searching {self.megajournal} for {keyword} in all years...")
            resp: SearchModel = self.search_single_page(
                logger=self.logger,
                keyword_year_pair=(keyword, 0),
                page=1,
            )

            paper_count: int = self._compute_total_number_of_papers(resp=resp)

            data.append(
                self.search_single_page(
                    logger=self.logger,
                    keyword_year_pair=(keyword, 0),
                    page=paper_count,
                )
            )

        return data

    def parse_response(self, responses: list[SearchModel]) -> list[ArticleModel]:
        data: list[ArticleModel] = []

        response_index: int = 0

        with Bar(
            "Extracting articles from search results...", max=len(responses)
        ) as bar:
            response: SearchModel
            for response in responses:
                docs: list[dict] = response.json_data["Articles"]

                doc: dict
                for doc in docs:
                    data.append(
                        ArticleModel(
                            doi=doc["Doi"],
                            title=doc["Title"],
                            megajournal=self.megajournal,
                            journal=doc["Journal"]["Title"],
                            search_id=response_index,
                        )
                    )

                response_index += 1
                bar.next()

        return data

    def download_jats(self, df: DataFrame, **kwargs) -> DataFrame:
        data: dict[str, list[str]] = {
            "doi": [],
            "jats_xml": [],
        }

        with Bar(
            "Downloading JATS XML content from FrontiersIn...",
            max=df.shape[0],
        ) as bar:
            row: Series
            for _, row in df.iterrows():
                oa_json: dict = loads(s=row["json_data"])
                open_access_pdf_url: str = oa_json["best_oa_location"]["pdf_url"]

                try:
                    xml_url: str = open_access_pdf_url.replace(
                        "/pdf",
                        "/xml",
                    )
                except AttributeError:
                    self.logger.debug("No url for %s", row["doi"])
                    bar.next()
                    continue

                self.logger.info("Getting JATS XML from: %s ...", xml_url)

                try:
                    resp: Response = self.session.get(url=xml_url, timeout=60)
                    self.logger.info("Response status code: %s ...", resp.status_code)
                    resp.raise_for_status()
                    data["doi"].append(row["doi"])
                    data["jats_xml"].append(resp.content.decode("UTF-8").strip("\n"))
                except HTTPError:
                    pass

                bar.next()

        return DataFrame(data=data)
