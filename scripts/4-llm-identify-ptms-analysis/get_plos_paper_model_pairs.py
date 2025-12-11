import json
from pathlib import Path

import pandas
from pandas import DataFrame

from aius.db.db import DB

json_file: Path = Path("../../data/gpt_oss/gpt-oss-20b_identify_ptms.json").resolve()
db: DB = DB(db_path=Path("../../data/aius_10-20-2025.sqlite3").resolve())

json_data: dict = json.load(fp=json_file.open())
df_data: dict[str, list[int | str]] = {
    "_id": [],
    "model": [],
}

key: str
val: list[dict]
for key, val in json_data.items():
    if len(val) == 0:
        continue

    if val[0]["model"] == "":
        continue

    if val[0]["model"] == None:
        continue

    datum: dict
    for datum in val:
        df_data["_id"].append(int(key))
        df_data["model"].append(datum["model"])

json_df: DataFrame = DataFrame(data=df_data)
db_df: DataFrame = pandas.read_sql(
    sql="""
                                   SELECT plos_natural_science_papers._id, plos_paper_dois.doi FROM plos_natural_science_papers
                                   JOIN plos_paper_dois on plos_natural_science_papers.plos_paper_id = plos_paper_dois._id;""",
    con=db.engine,
)

df = json_df.join(other=db_df, on="_id", lsuffix="_")
df = df.drop(columns="_id_").set_index(keys="_id")
df.to_csv(path_or_buf="model_paper_pairs.csv")
