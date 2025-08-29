from requests import Response
from aius.search import JournalSearch, SEARCH_RESULTS
from string import Template


class PLOS(JournalSearch):
    def __init__(self) -> None:
        # Initialize class variables
        self.name: str = "plos"
        self.initial_page: int = 1
        self.current_page: int = self.initial_page

        # Create search URL template
        self.search_url_template: Template = Template(
            template="https://journals.plos.org/plosone/dynamicSearch?filterStartDate=${year}-01-01&filterEndDate=${year}-12-31&resultsPerPage=100&q=${keyword}&sortOrder=DATE_NEWEST_FIRST&page=${page}&filterArticleTypes=Research Article&unfilteredQuery=${keyword}"  # noqa: E501
        )

    def _construct_url(self, year: int, keyword: str, page: int) -> str:
        return self.search_url_template.substitute(
            keyword=keyword,
            year=year,
            page=page,
        )

    def search_all_pages(self, year: int, keyword: str) -> list[Response]:
        data: dict[str, list] = SEARCH_RESULTS.copy()
