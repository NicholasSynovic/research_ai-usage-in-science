from string import Template

from pandas import DataFrame
from requests import Response

from aius.download import Downloader


class PLOS(Downloader):
    def __init__(self, paper_dois: DataFrame) -> None:
        super().__init__(paper_dois)

        self.jats_url_template: Template = Template(
            template="https://journals.plos.org/plosone/article/file?id=${doi_prefix_suffix}&type=manuscript"
        )
        self.pdf_url_template: Template = Template(
            template="https://journals.plos.org/plosone/article/file?id=${doi_prefix_suffix}&type=printable"
        )

    def create_jats_urls(self) -> None:
        print(self.paper_dois)

    def create_pdf_urls(self) -> None:
        pass

    def get_jats(self) -> Response:
        return Response()

    def get_pdfs(self) -> Response:
        return Response()
