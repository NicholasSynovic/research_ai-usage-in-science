import pickle
from pathlib import Path

import pandas
from pandas import DataFrame
from progress.bar import Bar
from requests import Response, get

OA_TOPICS_API: str = "https://api.openalex.org/topics"
PICKLE_PATH: Path = Path("oa_topics.pickle").absolute()


def get_all_pages(total_count: int = 4600, per_page: int = 100) -> DataFrame:
    dfs: list[DataFrame] = []

    pages: int = total_count // per_page

    with Bar("Getting OpenAlex Topics API...", max=pages) as bar:
        for idx in range(pages):
            resp: Response = get(
                url=f"{OA_TOPICS_API}?per-page={per_page}&page={idx + 1}",
                timeout=60,
            )
            dfs.append(DataFrame(data=resp.json()["results"]))
            bar.next()

    return pandas.concat(objs=dfs, ignore_index=True)


def main() -> None:
    # Load data if it exists else get the data
    df: DataFrame
    if PICKLE_PATH.exists():
        df = pickle.load(file=PICKLE_PATH.open(mode="rb"))
    else:
        df = get_all_pages()
        PICKLE_PATH.write_bytes(data=pickle.dumps(obj=df))

    print("Total topics:", df["id"].unique().size)
    print("Total subfields:", DataFrame(df["subfield"].to_list())["id"].unique().size)
    print("Total fields:", DataFrame(df["field"].to_list())["id"].unique().size)
    print("Total domains:", DataFrame(df["domain"].to_list())["id"].unique().size)


if __name__ == "__main__":
    main()
