import pickle
import zipfile
from pathlib import Path

import pandas
from bs4 import BeautifulSoup
from bs4.element import Tag
from pandas import DataFrame
from progress.bar import Bar

from aius.db import DB

sql_query: str = """
SELECT a.*
FROM papers a
JOIN ns_papers b ON a._id = b.paper_id;
"""

data: dict[str, list] = {"filename": [], "content": []}

all_of_plos_archive: Path = Path("../data/all_of_plos.zip").resolve()
db: DB = DB(db_path=Path("../AIUS.sqlite3").resolve())

df: DataFrame = pandas.read_sql_query(sql=sql_query, con=db.engine)
df = df[df["doi"].str.contains(pat="doi.org/10.1371")]
df["filename"] = df["doi"].str.replace(pat="https://doi.org/10.1371/", repl="") + ".xml"


with Bar("Converting JATS XML to MD (formatted)...", max=df["filename"].size) as bar:
    with zipfile.ZipFile(all_of_plos_archive, "r") as z:
        for file in df["filename"]:
            data["filename"].append(file)

            with z.open(file) as f:
                soup: BeautifulSoup = BeautifulSoup(
                    markup=f.read(),
                    features="lxml-xml",
                )

                soup.find(name="back").decompose()  # Remove citations
                soup.find(name="journal-meta").decompose()  # Remove journal

                # Remove all frontmatter except for the title and abstract
                frontmatter_tag: Tag = soup.find(name="article-meta")

                child_tag: Tag
                for child_tag in frontmatter_tag.children:
                    if child_tag.name == None:
                        continue

                    if child_tag.name == "title-group":
                        continue

                    if child_tag.name == "abstract":
                        continue

                    child_tag.decompose()

                text: str = soup.prettify()

                data["content"].append(text)
                f.close()

            bar.next()
        z.close()

with open(file="formatted_jats_tokens.pickle", mode="wb") as jt:
    pickle.dump(obj=data, file=jt)
