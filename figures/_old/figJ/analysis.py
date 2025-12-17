import json

import pandas
from pandas import DataFrame

df = pandas.read_parquet(
    "/home/nicholas/Documents/research_ai-usage-in-science/data/analysis/prompt_engineering-identify_reuse/gpt-oss-20b_identify_reuse.parquet"
)

print(df.columns)


df["json"] = df["response_text"].apply(json.loads)
df["json"].to_json("review_2.json", indent=4)
