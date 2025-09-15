import pickle
from pathlib import Path

import pandas
from pandas import DataFrame
from progress.bar import Bar
from requests import Response, get
from aius import FIELD_FILTER
from pandas.core.groupby import DataFrameGroupBy

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
    topic_df: DataFrame
    if PICKLE_PATH.exists():
        topic_df = pickle.load(file=PICKLE_PATH.open(mode="rb"))
    else:
        topic_df = get_all_pages()
        PICKLE_PATH.write_bytes(data=pickle.dumps(obj=topic_df))

    # Convert dict into DataFrames
    subfield_df: DataFrame = DataFrame(topic_df["subfield"].to_list())
    field_df: DataFrame = DataFrame(topic_df["field"].to_list())
    domain_df: DataFrame = DataFrame(topic_df["domain"].to_list())

    # Output counts of each category
    print("Total topics:", topic_df["id"].unique().size)
    print("Total subfields:", subfield_df["id"].unique().size)
    print("Total fields:", field_df["id"].unique().size)
    print("Total domains:", domain_df["id"].unique().size)

    # Create DataFrame where it is just the names of the attributes + topic works count
    topic_df["subfield_name"] = topic_df["subfield"].apply(lambda x: x["display_name"])
    topic_df["field_name"] = topic_df["field"].apply(lambda x: x["display_name"])
    topic_df["domain_name"] = topic_df["domain"].apply(lambda x: x["display_name"])
    df: DataFrame = topic_df[["display_name", "works_count", "subfield_name", "field_name", "domain_name",]]

    # Filter for only Natural Science topics
    ns_df = df[df["field_name"].isin(FIELD_FILTER)]

    # Count the number of Natural Science topics, subfields, fields, and domains
    print("Natural Science topics:", ns_df["display_name"].unique().size)
    print("Natural Science subfields:", ns_df["subfield_name"].unique().size)
    print("Natural Science fields:", ns_df["field_name"].unique().size)
    print("Natural Science domains:", ns_df["domain_name"].unique().size)

    # Count the number of topics and subfields per field
    ns_dfgb: DataFrameGroupBy = ns_df.groupby(by="field_name")

    _df: DataFrame
    idx: str
    for idx, _df in ns_dfgb:
        print(idx, "topics", _df["display_name"].unique().size, "subfields", _df["subfield_name"].unique().size,)


if __name__ == "__main__":
    main()
