import pickle
from pathlib import Path

import pandas
from pandas import DataFrame
from progress.bar import Bar
from requests import Response, get

from aius import KEYWORD_LIST, YEAR_LIST
from aius.search.plos import PLOS

PICKLE_PATH: Path = Path("plos_pilot_papers.pickle").absolute()


def get_all_pages(urls: list[str]) -> DataFrame:
    dfs: list[DataFrame] = []

    with Bar("Getting PLOS pilot study pages...", max=len(urls)) as bar:
        for url in urls:
            resp: Response = get(
                url=url,
                timeout=60,
            )
            dfs.append(DataFrame(data=resp.json()["searchResults"]["docs"]))
            bar.next()

    return pandas.concat(objs=dfs, ignore_index=True)


def create_urls() -> list[str]:
    urls: list[str] = []
    plos: PLOS = PLOS()

    year: int
    keyword: str
    for year in YEAR_LIST:
        for keyword in KEYWORD_LIST:
            urls.append(
                plos._construct_url(year=year, keyword=keyword, page=1)
                .replace("DATE_NEWEST_FIRST", "MOST_CITED")
                .replace("resultsPerPage=100", "resultsPerPage=5")
            )

    return urls


def main() -> None:
    # Load data if it exists else get the data
    df: DataFrame
    if PICKLE_PATH.exists():
        df = pickle.load(file=PICKLE_PATH.open(mode="rb"))
    else:
        urls: list[str] = create_urls()
        df = get_all_pages(urls=urls)
        PICKLE_PATH.write_bytes(data=pickle.dumps(obj=df))

    print(df["id"].unique().size)


if __name__ == "__main__":
    main()
