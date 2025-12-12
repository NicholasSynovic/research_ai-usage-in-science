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
