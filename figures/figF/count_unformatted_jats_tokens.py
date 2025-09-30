import pickle
import zipfile
from pathlib import Path

import pandas
import tiktoken
from pandas import DataFrame
from progress.bar import Bar

from aius.db import DB

sql_query: str = """
SELECT a.*
FROM papers a
JOIN ns_papers b ON a._id = b.paper_id;
"""

data: dict[str, list] = {"filename": [], "tokens": [], "content": []}

all_of_plos_archive: Path = Path("../data/all_of_plos.zip").resolve()
db: DB = DB(db_path=Path("../AIUS.sqlite3").resolve())

encoding = tiktoken.encoding_for_model("gpt-4")

df: DataFrame = pandas.read_sql_query(sql=sql_query, con=db.engine)
df = df[df["doi"].str.contains(pat="doi.org/10.1371")]
df["filename"] = df["doi"].str.replace(pat="https://doi.org/10.1371/", repl="") + ".xml"


with Bar("Computing tokens...", max=df["filename"].size) as bar:
    with zipfile.ZipFile(all_of_plos_archive, "r") as z:
        for file in df["filename"]:
            data["filename"].append(file)

            with z.open(file) as f:
                text: str = (
                    f.read().decode("utf-8").replace("\n", "")
                )  # convert bytes → string
                data["tokens"].append(len(encoding.encode(text=text)))
                data["content"].append(text)
                f.close()

            bar.next()
        z.close()

with open(file="unformatted_jats_tokens.pickle", mode="wb") as jt:
    pickle.dump(obj=data, file=jt)
