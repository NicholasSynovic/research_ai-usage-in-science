from logging import Logger
from pathlib import Path

import pandas
from pandas import DataFrame
from requests import Session
from requests.adapters import HTTPAdapter, Retry

from aius.db import DB
from aius.runners.runner import Runner


class JATS(Runner):
    def __init__(self, logger: Logger, db: DB, plos_zip_fp: Path) -> None:
        # Set class constants
        self.logger: Logger = logger
        self.db: DB = db
        self.plos_zip_fp: Path = plos_zip_fp

        # Custom HTTPS session with exponential backoff enabled
        self.session: Session = Session()
        self.session.mount(
            "https://",
            HTTPAdapter(
                max_retries=Retry(total=10, backoff_factor=1),
            ),
        )

    def get_data(self) -> DataFrame:
        sql: str = """
SELECT
    ns.doi, a.megajournal
FROM
    natural_science_article_dois ns
JOIN
    articles a
ON
    a.doi = ns.doi;"""

        return pandas.read_sql(sql=sql, con=self.db.engine)

    def execute(self) -> int:
        # Get data from the database
        df: DataFrame = self.get_data()

        # Add doi URI
        df["doi"] = "https://doi.org/" + df["doi"]

        print(df)

        return 0
