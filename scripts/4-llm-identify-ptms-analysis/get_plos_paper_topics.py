from collections import defaultdict
from pathlib import Path

import pandas
from pandas import DataFrame, Series

from aius.db import DB

csv_file: Path = Path("model_paper_pairs.csv").resolve()
db: DB = DB(db_path=Path("../../data/aius_10-20-2025.sqlite3").resolve())

csv_df: DataFrame = pandas.read_csv(filepath_or_buffer=csv_file)


db_df: DataFrame = pandas.read_sql(
    sql="""
                                   SELECT plos_natural_science_papers._id, plos_paper_openalex_metadata.topic_0, plos_paper_openalex_metadata.topic_1, plos_paper_openalex_metadata.topic_2 FROM plos_natural_science_papers
JOIN plos_paper_openalex_metadata on plos_natural_science_papers.plos_paper_id = plos_paper_openalex_metadata.plos_paper_id;""",
    con=db.engine,
)

df = csv_df.join(other=db_df, on="_id", lsuffix="_")
df = df.drop(columns="_id_").set_index(keys="_id")
# df.to_csv(path_or_buf="topic_model_pairs.csv", sep="|")

data: dict[str, dict[str, int]] = {
    "audio": defaultdict(int),
    "graph": defaultdict(int),
    "multimodal": defaultdict(int),
    "text": defaultdict(int),
    "vision": defaultdict(int),
}
for _, row in df.iterrows():
    datum: set[str] = set([row["topic_0"], row["topic_1"], row["topic_2"]])

    for topic in datum:
        data[row["type"]][topic] += 1

from pprint import pprint as print

print(data)
