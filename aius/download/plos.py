from string import Template

from pandas import DataFrame

from aius.download import Downloader


class PLOS(Downloader):
    def __init__(self, paper_dois: DataFrame) -> None:
        super().__init__(paper_dois)

        self.html_url_template: Template = Template(
            template="https://journals.plos.org/plosone/article/file?id=${doi_prefix_suffix}"
        )
        self.jats_url_template: Template = Template(
            template="https://journals.plos.org/plosone/article/file?id=${doi_prefix_suffix}&type=manuscript"
        )
        self.pdf_url_template: Template = Template(
            template="https://journals.plos.org/plosone/article/file?id=${doi_prefix_suffix}&type=printable"
        )
