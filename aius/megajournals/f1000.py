from datetime import datetime, timezone
from itertools import product
from logging import Logger
from string import Template

from bs4 import BeautifulSoup, ResultSet, Tag
from pandas import DataFrame, Series
from progress.bar import Bar
from requests import HTTPError, Response

from aius.db import DB
from aius.megajournals.megajournal import MegaJournal
from aius.megajournals.models import ArticleModel, SearchModel


class F1000(MegaJournal):
    def __init__(self, logger: Logger, db: DB) -> None:
        # Load default variable values
        super().__init__(logger=logger, db=db)

        self.megajournal: str = "F1000"
        self.search_url_template: Template = Template(
            template="https://f1000research.com/extapi/search?page=${page}&rows=100&start=0&q=R_TE:${query} AND R_PUD:%5B${t1} TO ${t2}%5D&wt=json"
        )

        self.keyword_year_products: product = product(
            self.db.get_search_keywords(),
            self.db.get_years(),
        )

        self.logger.info(msg=f"Mega Journal: {self.megajournal}")
        self.logger.info(msg=f"Keyword-Year products: {self.keyword_year_products}")

    def search_single_page(
        self,
        logger: Logger,
        keyword_year_pair: tuple[str, int],
        page: int = 1,
    ) -> SearchModel:
        timestamp: float = datetime.now(tz=timezone.utc).timestamp()
        t1: int = (
            int(datetime(year=keyword_year_pair[1], month=1, day=1).timestamp()) * 1000
        )
        t2: int = (
            int(datetime(year=keyword_year_pair[1], month=12, day=31).timestamp())
            * 1000
        )

        url: str = self.search_url_template.substitute(
            query=keyword_year_pair[0],
            t1=t1,
            t2=t2,
            page=page,
        )
        logger.info(msg=f"Search URL: {url}")

        timestamp: float = datetime.now(tz=timezone.utc).timestamp()
        resp: Response = self.session.get(url=url, timeout=self.timeout)
        logger.debug(msg=f"Response status code: {resp.status_code}")

        if resp.status_code != 200:
            logger.error(msg=f"Non 200 response code: {resp.content}")

        logger.debug(f"URL: {url}")

        return SearchModel(
            timestamp=timestamp,
            megajournal=self.megajournal,
            search_keyword=keyword_year_pair[0],
            status_code=resp.status_code,
            year=keyword_year_pair[1],
            page=page,
            url=url,
            json_data={"xml": resp.content.decode(encoding="UTF-8")},
        )

    def _compute_total_number_of_pages(self, resp: SearchModel) -> int:
        document_count: int = 1
        soup: BeautifulSoup = BeautifulSoup(
            markup=resp.json_data["xml"],
            features="lxml",
        )

        self.logger.debug(soup.prettify())

        document_count_tag: Tag | None = soup.find(name="results")

        if isinstance(document_count_tag, Tag):
            try:
                document_count = int(document_count_tag["totalnumberofpages"])
            except ValueError:
                pass

        return document_count

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

                self.logger.debug(f"Page count {page_count}")

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
                soup: BeautifulSoup = BeautifulSoup(
                    markup=response.json_data["xml"],
                    features="lxml",
                )

                docs: ResultSet[Tag] = soup.find_all(name="doi")

                doc: Tag
                for doc in docs:
                    data.append(
                        ArticleModel(
                            doi=doc.text,
                            title="",
                            megajournal=self.megajournal,
                            journal="",
                            search_id=response_index,
                        )
                    )

                response_index += 1
                bar.next()

        return data

    def download_jats(self, df: DataFrame, **kwargs) -> DataFrame:  # noqa: D102
        data: dict[str, list[str]] = {
            "doi": [],
            "jats_xml": [],
        }

        with Bar(
            "Downloading JATS XML content from F1000...",
            max=df.shape[0],
        ) as bar:
            row: Series
            for _, row in df.iterrows():
                xml_url: str = (
                    f"https://f1000research.com/extapi/article/xml?doi={row['doi']}"
                )
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
