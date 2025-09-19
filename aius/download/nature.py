from string import Template

from pandas import DataFrame

from aius.download import Downloader


class Nature(Downloader):
    def __init__(self, paper_dois: DataFrame) -> None:
        super().__init__(paper_dois)

        self.html_url_template: Template = Template(
            template="https://www.nature.com/articles/{doi_suffix}"
        )
        self.pdf_url_template: Template = Template(
            template="https://www.nature.com/articles/{doi_suffix}.pdf"
        )

    def create_html_urls(self) -> None:
        self.paper_dois["html_url"] = self.paper_dois["doi"].apply(
            lambda x: self.jats_url_template.substitute(
                doi_prefix_suffix=x.replace("https://doi.org/10.1038/", ""),
            )
        )

    def create_jats_urls(self) -> None:
        self.paper_dois["jats_url"] = self.paper_dois["doi"].apply(
            lambda x: self.jats_url_template.substitute(
                doi_prefix_suffix=x.replace("https://doi.org/10.1038/", ""),
            )
        )

    def create_pdf_urls(self) -> None:
        self.paper_dois["pdf_url"] = self.paper_dois["doi"].apply(
            lambda x: self.pdf_url_template.substitute(
                doi_prefix_suffix=x.replace("https://doi.org/10.1038/", ""),
            )
        )
