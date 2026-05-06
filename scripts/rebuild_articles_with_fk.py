"""
Load the `searches` table from a SQLite database and print it.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from json import loads
from logging import Logger
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup, ResultSet, Tag
from progress.bar import Bar
from sqlalchemy import create_engine, text

from aius.db import DB
from aius.megajournals import MEGAJOURNAL_MAPPING
from aius.megajournals.megajournal import MegaJournal
from aius.megajournals.models import ArticleModel, SearchModel


def bmj_parse_response(df: pd.DataFrame) -> list[ArticleModel]:
    data: list[ArticleModel] = []

    with Bar("Extracting articles from search results...", max=df.shape[0]) as bar:
        row: pd.Series
        for _, row in df.iterrows():
            soup: BeautifulSoup = BeautifulSoup(
                markup=row["json_data"]["html"],
                features="lxml",
            )

            docs: ResultSet[Tag] = soup.find_all(
                name="div",
                attrs={
                    "class": "highwire-cite-highwire-article",
                },
            )

            doc: Tag
            for doc in docs:
                doi_tag: Tag | None = doc.find(
                    name="span",
                    attrs={
                        "class": "highwire-cite-metadata-doi",
                    },
                )
                title_tag: Tag | None = doc.find(
                    name="span",
                    attrs={
                        "class": "highwire-cite-title",
                    },
                )
                journal_tag: Tag | None = doc.find(
                    name="span",
                    attrs={
                        "class": "highwire-cite-metadata-journal",
                    },
                )

                if not isinstance(doi_tag, Tag):
                    continue

                if not isinstance(title_tag, Tag):
                    continue

                if not isinstance(journal_tag, Tag):
                    continue

                data.append(
                    ArticleModel(
                        doi=doi_tag.text.split(" ")[1],
                        title=title_tag.text,
                        megajournal="BMJ",
                        journal=journal_tag.text,
                        search_id=row["_id"],
                    )
                )
            bar.next()
    return data


def f1000_parse_response(df: pd.DataFrame) -> list[ArticleModel]:
    data: list[ArticleModel] = []

    with Bar("Extracting articles from search results...", max=df.shape[0]) as bar:
        row: pd.Series
        for _, row in df.iterrows():
            soup: BeautifulSoup = BeautifulSoup(
                markup=row["json_data"]["xml"],
                features="lxml",
            )

            docs: ResultSet[Tag] = soup.find_all(name="doi")

            doc: Tag
            for doc in docs:
                data.append(
                    ArticleModel(
                        doi=doc.text,
                        title="",
                        megajournal="F1000",
                        journal="",
                        search_id=row["_id"],
                    )
                )

            bar.next()
    return data


def frontiersin_parse_response(df: pd.DataFrame) -> list[ArticleModel]:
    data: list[ArticleModel] = []

    with Bar("Extracting articles from search results...", max=df.shape[0]) as bar:
        row: pd.Series
        for _, row in df.iterrows():
            docs: list[dict] = row["json_data"]["Articles"]

            doc: dict
            for doc in docs:
                data.append(
                    ArticleModel(
                        doi=doc["Doi"],
                        title=doc["Title"],
                        megajournal="FrontiersIn",
                        journal=doc["Journal"]["Title"],
                        search_id=row["_id"],
                    )
                )

            bar.next()
    return data


def plos_parse_response(df: pd.DataFrame) -> list[ArticleModel]:
    data: list[ArticleModel] = []

    with Bar("Extracting articles from search results...", max=df.shape[0]) as bar:
        row: pd.Series
        for _, row in df.iterrows():
            docs: list[dict] = row["json_data"]["searchResults"]["docs"]

            doc: dict
            for doc in docs:
                data.append(
                    ArticleModel(
                        doi=doc["id"],
                        title=doc["title"],
                        megajournal="PLOS",
                        journal=doc["journal_name"],
                        search_id=row["_id"],
                    )
                )

            bar.next()
    return data


def read_table(engine) -> pd.DataFrame:
    df = pd.read_sql_query(sql=text("SELECT * FROM searches;"), con=engine)
    df["json_data"] = df["json_data"].apply(loads)
    return df


def df_to_searchmodel(df: pd.DataFrame) -> dict[str, list[SearchModel]]:
    data: dict[str, list[SearchModel]] = defaultdict(list)

    row: pd.Series
    for _, row in df.iterrows():
        data[row["megajournal"].lower()].append(SearchModel(**row))

    return data


def parse_searches_for_articles(searches: pd.DataFrame) -> list[ArticleModel]:
    data: list[ArticleModel] = []

    keys: set[str] = set(searches["megajournal"].str.lower().tolist())
    key: str
    for key in keys:
        match key:
            case "bmj":
                data.extend(
                    bmj_parse_response(searches[searches["megajournal"] == "BMJ"])
                )
            case "f1000":
                data.extend(
                    f1000_parse_response(searches[searches["megajournal"] == "F1000"])
                )
            case "frontiersin":
                data.extend(
                    frontiersin_parse_response(
                        searches[searches["megajournal"] == "FrontiersIn"]
                    )
                )
            case "plos":
                data.extend(
                    plos_parse_response(searches[searches["megajournal"] == "PLOS"])
                )

    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("db_path", type=Path)
    args = parser.parse_args()

    db_path = args.db_path.resolve()
    engine = create_engine(f"sqlite:///{db_path}")
    searches_df = read_table(engine)

    articlemodels: list[ArticleModel] = parse_searches_for_articles(searches_df)
    article_df: pd.DataFrame = pd.concat(
        objs=[a.to_df for a in articlemodels], ignore_index=True
    )

    article_df.to_sql(
        name="articles", con=engine, if_exists="append", index=True, index_label="_id"
    )


if __name__ == "__main__":
    main()
