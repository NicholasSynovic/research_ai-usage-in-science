"""
JATS XML download runner.

Copyright 2025 (C) Nicholas M. Synovic

"""

from json import loads
from logging import Logger
from pathlib import Path
from zipfile import ZipFile

import pandas as pd
from bs4 import BeautifulSoup
from pandas import DataFrame, Series
from progress.bar import Bar
from requests import Response, Session
from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import HTTPError

from aius.db import DB
from aius.runners.runner import Runner


class JATSRunner(Runner):  # noqa: D101
    def __init__(  # noqa: D107
        self,
        logger: Logger,
        db: DB,
        plos_zip_fp: Path,
    ) -> None:
        # Set class constants
        self.logger: Logger = logger
        self.db: DB = db
        self.plos_zip_fp: Path = plos_zip_fp

        # Custom HTTPS session with exponential backoff enabled
        self.session: Session = Session()
        self.session.mount(
            "https://",
            HTTPAdapter(
                max_retries=Retry(total=5, backoff_factor=1),
            ),
        )

    def get_data(self) -> DataFrame:  # noqa: D102
        sql: str = """
SELECT ns.doi, a.megajournal, oa.json_data
FROM natural_science_article_dois ns
JOIN articles a ON a.doi = ns.doi
JOIN openalex oa ON oa.doi = ns.doi;
"""

        return pd.read_sql(sql=sql, con=self.db.engine)

    def extract_plos_jats(self, df: DataFrame) -> DataFrame:  # noqa: D102
        data: dict[str, list[str | int]] = {
            "doi": [],
            "jats_xml": [],
        }

        with (
            Bar(
                "Extracting JATS XML content from PLOS zip archive...",
                max=df.shape[0],
            ) as bar,
            ZipFile(file=self.plos_zip_fp, mode="r") as zf,
        ):
            # For each filename, open the file's content and add it to the
            # data structure
            row: Series
            for _, row in df.iterrows():
                # Open the file and decode the content
                filename: str = row["doi"].split("/")[1] + ".xml"
                with zf.open(name=filename, mode="r") as fp:
                    data["doi"].append(row["doi"])

                    # Add prettified JATS XML to the data structure
                    data["jats_xml"].append(
                        BeautifulSoup(
                            markup=fp.read().decode("UTF-8").strip("\n"),
                            features="lxml",
                        ).prettify()
                    )

                    fp.close()
                bar.next()
            zf.close()

        return DataFrame(data=data)

    def download_bmj(self, df: DataFrame) -> DataFrame:  # noqa: D102
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
                    resp: Response = self.session.get(url=xml_url, timeout=60)
                    self.logger.info("Response status code: %s ...", resp.status_code)
                    resp.raise_for_status()
                    data["doi"].append(row["doi"])
                    data["jats_xml"].append(resp.content.decode("UTF-8").strip("\n"))
                except HTTPError:
                    pass

                bar.next()

        return DataFrame(data=data)

    def download_f1000(self, df: DataFrame) -> DataFrame:  # noqa: D102
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

    def download_frontiersin(self, df: DataFrame) -> DataFrame:  # noqa: D102
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

    def execute(self) -> int:  # noqa: D102
        # Get data from the database
        df: DataFrame = self.get_data()

        # Split the dataframe by megajournal
        bmj_df: DataFrame = df[df["megajournal"] == "BMJ"].copy()
        f1000_df: DataFrame = df[df["megajournal"] == "F1000"].copy()
        frontiersin_df: DataFrame = df[df["megajournal"] == "FrontiersIn"].copy()
        plos_df: DataFrame = df[df["megajournal"] == "PLOS"].copy()

        bmj_jats: DataFrame = self.download_bmj(df=bmj_df)
        f1000_jats: DataFrame = self.download_f1000(df=f1000_df)
        frontiersin_jats: DataFrame = self.download_frontiersin(df=frontiersin_df)
        plos_jats: DataFrame = self.extract_plos_jats(df=plos_df)

        jats_df: DataFrame = pd.concat(
            objs=[
                bmj_jats,
                f1000_jats,
                frontiersin_jats,
                plos_jats,
            ],
            ignore_index=True,
        )

        self.db.write_dataframe_to_table(table_name="jats", df=jats_df)

        return 0
