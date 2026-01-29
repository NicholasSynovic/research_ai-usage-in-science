from datetime import datetime, timezone
from itertools import product
from json import loads
from logging import Logger
from math import ceil
from string import Template

from bs4 import BeautifulSoup, ResultSet, Tag
from pandas import DataFrame, Series
from progress.bar import Bar
from requests import HTTPError, Response, get

from aius.db import DB
from aius.megajournals.megajournal import MegaJournal
from aius.megajournals.models import ArticleModel, SearchModel


class BMJ(MegaJournal):
    def __init__(self, logger: Logger, db: DB) -> None:
        # Load default variable values
        super().__init__(logger=logger, db=db)

        self.megajournal: str = "BMJ"
        self.search_url_template: Template = Template(
            template="https://journals.bmj.com/search/${query} limit_from:${year}-01-01 limit_to:${year}-12-31 jcode:bmjcimm||bmjdhai||bmjgh||bmjhci||bmjmed||bmjno||bmjnph||bmjonc||bmjopen||bmjph||bmjdrc||bmjgast||bmjophth||bmjqir||bmjresp||bmjosem||bmjpo||bmjccgg||bmjconc||bmjsit||egastro||fmch||gocm||gpsych||jmepb||jitc||lupusscimed||openhrt||rmdopen||svnbmj||tsaco||wjps exclude_meeting_abstracts:0 numresults:100 sort:publication-date direction:descending format_result:standard button:Submit button2:Submit button3:Submit?page=${page}"
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
        url: str = self.search_url_template.substitute(
            query=keyword_year_pair[0],
            year=keyword_year_pair[1],
            page=page,
        )
        logger.info(msg=f"Search URL: {url}")

        timestamp: float = datetime.now(tz=timezone.utc).timestamp()
        resp: Response = self.session.get(
            url=url,
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
            url=url,
            json_data={"html": resp.content.decode(encoding="UTF-8")},
        )

    def _compute_total_number_of_pages(self, resp: SearchModel) -> int:
        document_count: int = 1
        soup: BeautifulSoup = BeautifulSoup(
            markup=resp.json_data["html"],
            features="lxml",
        )

        document_count_tag: Tag | None = soup.find(
            name="div",
            attrs={
                "id": "search-summary-wrapper",
                "class": "highwire-search-summary",
            },
        )

        if isinstance(document_count_tag, Tag):
            try:
                document_count = int(document_count_tag.text.split(" ")[0])
            except ValueError:
                pass

        return ceil(document_count / 100)

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
                soup: BeautifulSoup = BeautifulSoup(
                    markup=response.json_data["html"],
                    features="lxml",
                )

                docs: ResultSet[Tag] = soup.find_all(
                    name="div",
                    attrs={
                        "class": "highwire-cite-highwire-article",
                    },
                )

                doc: Tag
                for doc in docs:
                    doi_tag: Tag | None = doc.find(
                        name="span",
                        attrs={
                            "class": "highwire-cite-metadata-doi",
                        },
                    )
                    title_tag: Tag | None = doc.find(
                        name="span",
                        attrs={
                            "class": "highwire-cite-title",
                        },
                    )
                    journal_tag: Tag | None = doc.find(
                        name="span",
                        attrs={
                            "class": "highwire-cite-metadata-journal",
                        },
                    )

                    if not isinstance(doi_tag, Tag):
                        continue

                    if not isinstance(title_tag, Tag):
                        continue

                    if not isinstance(journal_tag, Tag):
                        continue

                    data.append(
                        ArticleModel(
                            doi=doi_tag.text.split(" ")[1],
                            title=title_tag.text,
                            megajournal=self.megajournal,
                            journal=journal_tag.text,
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
            "Downloading JATS XML content from BMJ...",
            max=df.shape[0],
        ) as bar:
            row: Series
            for _, row in df.iterrows():
                oa_json: dict = loads(s=row["json_data"])
                open_access_pdf_url: str = oa_json["best_oa_location"]["pdf_url"]

                try:
                    xml_url: str = open_access_pdf_url.replace(
                        ".full.pdf",
                        ".download.xml",
                    )
                except AttributeError:
                    self.logger.debug("No url for %s", row["doi"])
                    bar.next()
                    continue

                self.logger.info("Getting JATS XML from: %s ...", xml_url)

                try:
                    # Doesn't use self.session
                    resp: Response = get(url=xml_url, timeout=60)
                    self.logger.info("Response status code: %s ...", resp.status_code)
                    resp.raise_for_status()
                    data["doi"].append(row["doi"])
                    data["jats_xml"].append(resp.content.decode("UTF-8").strip("\n"))
                except HTTPError:
                    self.logger.error("HTTPError with: %s ...", xml_url)

                bar.next()

        return DataFrame(data=data)
