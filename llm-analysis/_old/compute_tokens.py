import math
import statistics

import pandas
import tiktoken
from pandas import DataFrame

num: list[int] = []

df: DataFrame = pandas.read_parquet(path="../data/pdf_preprocessing.parquet")

for _, row in df.iterrows():
    text: str = "".join(row["document_text"])
    encoding = tiktoken.encoding_for_model("gpt-4")

    encoded_token_count: int = math.floor(len(encoding.encode(text=text)) / 100) * 100
    num.append(encoded_token_count)

print("mean", statistics.mean(data=num))
print("median", statistics.median(data=num))
print("max", max(num))
print("min", min(num))
print("mode", statistics.mode(data=num))
