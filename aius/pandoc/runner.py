"""
Document conversion with `pandoc` runner.

Copyright 2025 (C) Nicholas M. Synovic

"""

from logging import Logger

import pandas as pd
from bs4 import BeautifulSoup, ResultSet, Tag
from mdformat import text
from pandas import DataFrame, Series
from progress.bar import Bar
from requests import Response, post

from aius.db import DB
from aius.runner import Runner


class PandocRunner(Runner):  # noqa: D101
    def __init__(self, logger: Logger, db: DB, pandoc_uri: str) -> None:  # noqa: D107
        super().__init__(name="pandoc", db=db, logger=logger)

        # Set class constants
        self.pandoc_uri: str = pandoc_uri
        self.json_body: dict[str, str] = {
            "from": "jats",
            "to": "markdown",
            "text": "",
        }

    @staticmethod
    def format_xml(xml: str) -> str:  # noqa: D102
        soup: BeautifulSoup = BeautifulSoup(markup=xml, features="lxml")

        front_tag: Tag | None = soup.find(name="front")
        back_tag: Tag | None = soup.find(name="back")
        xref_tags: ResultSet[Tag] = soup.find_all(name="xref")

        if isinstance(front_tag, Tag):
            front_tag.clear()

        if isinstance(back_tag, Tag):
            back_tag.clear()

        xref_tag: Tag
        for xref_tag in xref_tags:
            xref_tag.decompose()

        return soup.prettify()

    def execute(self) -> int:  # noqa: D102
        data: dict[str, list[str]] = {"doi": [], "markdown": []}

        df: DataFrame = pd.read_sql_table(
            table_name="jats",
            con=self.db.engine,
            index_col="_id",
        )

        with Bar("Converting JATS XML to Markdown...", max=df.shape[0]) as bar:
            row: Series
            for _, row in df.iterrows():
                data["doi"].append(row["doi"])

                xml: str = self.format_xml(xml=row["jats_xml"])
                self.json_body["text"] = xml

                self.logger.info("Converting %s from JATS XML to Markdown", row["doi"])
                resp: Response = post(
                    url=self.pandoc_uri,
                    json=self.json_body,
                    timeout=3600,
                )

                data["markdown"].append(text(md=resp.content.decode(encoding="utf-8")))

                bar.next()

        df: DataFrame = DataFrame(data=data)

        self.db.write_dataframe_to_table(table_name="markdown", df=df)

        return 0
