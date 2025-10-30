from pathlib import Path

import pandas
from pandas import DataFrame
from pandas.core.groupby import DataFrameGroupBy

df: DataFrame = pandas.read_csv(Path("model_paper_pairs.csv")).sort_values(
    by="model_doi"
)
dfgb: DataFrameGroupBy = df.groupby(by="model_doi")

data: dict[str, list[str | int]] = {
    "doi": [],
    "count": [],
    "model": [],
    "type": [],
}

for doi, _df in dfgb:
    data["doi"].append(doi)
    data["count"].append(_df.shape[0])
    data["model"].append(_df.reset_index(drop=True)["model"][0])
    data["type"].append(_df.reset_index(drop=True)["type"][0])

data_df: DataFrame = DataFrame(data=data).sort_values(by="count", ascending=False)[0:10]
print(data_df)
