from logging import Logger

import pandas
from mdformat import text
from pandas import DataFrame, Series
from progress.bar import Bar
from requests import Response, post

from aius.db import DB
from aius.runners.runner import Runner


class PandocRunner(Runner):
    def __init__(self, logger: Logger, db: DB, pandoc_uri: str) -> None:
        # Set class constants
        self.logger: Logger = logger
        self.db: DB = db
        self.pandoc_uri: str = pandoc_uri
        self.json_body: dict[str, str] = {
            "from": "jats",
            "to": "markdown",
            "text": "",
        }

    def get_data(self) -> DataFrame:
        return pandas.read_sql_table(
            table_name="jats",
            con=self.db.engine,
            index_col="_id",
        )

    def _write_data_to_table(self, table: str, data: DataFrame) -> None:
        self.logger.info(msg=f"Writing data to the `{table}` table")
        self.logger.debug(msg=f"Data: {data}")
        data.to_sql(
            name=table,
            con=self.db.engine,
            if_exists="append",
            index=True,
            index_label="_id",
        )
        self.logger.info(msg=f"Wrote data to the `{table}` table")

    def execute(self) -> int:
        data: dict[str, list[str]] = {"doi": [], "markdown": []}

        df: DataFrame = self.get_data()

        with Bar("Converting JATS XML to Markdown...", max=df.shape[0]) as bar:
            row: Series
            for _, row in df.iterrows():
                data["doi"].append(row["doi"])

                self.json_body["text"] = row["jats"]

                resp: Response = post(
                    url=self.pandoc_uri,
                    json=self.json_body,
                    timeout=3600,
                )

                data["markdown"].append(text(md=resp.content.decode(encoding="utf-8")))

                bar.next()

        df: DataFrame = DataFrame(data=data)

        self._write_data_to_table(table="markdown", data=df)

        return 0
