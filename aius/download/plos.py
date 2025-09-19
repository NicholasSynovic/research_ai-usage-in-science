from pathlib import Path
from string import Template

from pandas import DataFrame

from aius.download import Downloader


class PLOS(Downloader):
    def __init__(self, paper_dois: DataFrame, output_dir: Path) -> None:
        super().__init__(paper_dois, output_dir=output_dir)

        self.html_url_template: Template = Template(
            template="https://journals.plos.org/plosone/article/file?id=${doi_prefix_suffix}"
        )
        self.jats_url_template: Template = Template(
            template="https://journals.plos.org/plosone/article/file?id=${doi_prefix_suffix}&type=manuscript"
        )
        self.pdf_url_template: Template = Template(
            template="https://journals.plos.org/plosone/article/file?id=${doi_prefix_suffix}&type=printable"
        )

    def create_html_urls(self) -> None:
        self.paper_dois["html_url"] = self.paper_dois["doi"].apply(
            lambda x: self.html_url_template.substitute(
                doi_prefix_suffix=x.replace("https://doi.org/", ""),
            )
        )

    def create_jats_urls(self) -> None:
        self.paper_dois["jats_url"] = (
            self.paper_dois["doi"]
            .copy()
            .apply(
                lambda x: self.jats_url_template.substitute(
                    doi_prefix_suffix=x.replace("https://doi.org/", ""),
                )
            )
        )

    def create_pdf_urls(self) -> None:
        self.paper_dois["pdf_url"] = (
            self.paper_dois["doi"]
            .copy()
            .apply(
                lambda x: self.pdf_url_template.substitute(
                    doi_prefix_suffix=x.replace("https://doi.org/", ""),
                )
            )
        )
