from itertools import product
from logging import Logger
from string import Template

from aius.db import DB
from aius.search.megajournal import MegaJournal, SearchModel


class BMJ(MegaJournal):
    def __init__(self, logger: Logger, db: DB) -> None:
        self.logger: Logger = logger

        # Load default variable values
        super().__init__()

        # Set constants
        self.db = db
        self.megajournal: str = "BMJ"
        self.search_url: Template = Template(template='https://journals.bmj.com/search/${query} limit_from:${year}-01-01 limit_to:${year}-12-31 jcode:bmjcimm||bmjdhai||bmjgh||bmjhci||bmjmed||bmjno||bmjnph||bmjonc||bmjopen||bmjph||bmjdrc||bmjgast||bmjophth||bmjqir||bmjresp||bmjosem||bmjpo||bmjccgg||bmjconc||bmjsit||egastro||fmch||gocm||gpsych||jmepb||jitc||lupusscimed||openhrt||rmdopen||svnbmj||tsaco||wjps exclude_meeting_abstracts:0 numresults:100 sort:publication-date direction:descending format_result:standard button:Submit button2:Submit button3:Submit?page=${page}')

        self.keyword_year_products: product = product(
            self.db.get_search_keywords(),
            self.db.get_years(),
        )

        self.logger.info(msg=f"Mega Journal: {self.megajournal}")
        self.logger.info(msg=f"Keyword-Year products: {self.keyword_year_products}")

def search_single_page(self, keyword_year_pair:tuple [str, int], page=1,)    ->  SearchModel:
    pass


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
url: str = 'https://journals.bmj.com/search/"Deep+Learning" limit_from:2022-01-01 limit_to:2022-12-31 jcode:bmjcimm||bmjdhai||bmjgh||bmjhci||bmjmed||bmjno||bmjnph||bmjonc||bmjopen||bmjph||bmjdrc||bmjgast||bmjophth||bmjqir||bmjresp||bmjosem||bmjpo||bmjccgg||bmjconc||bmjsit||egastro||fmch||gocm||gpsych||jmepb||jitc||lupusscimed||openhrt||rmdopen||svnbmj||tsaco||wjps exclude_meeting_abstracts:1 numresults:100 sort:publication-date direction:descending format_result:standard button:Submit button2:Submit button3:Submit'
