from itertools import product
from typing import List, Tuple

import pandas
from pandas import DataFrame

from src import SEARCH_KEYWORDS, YEARS
from src.journals.nature import Nature
from src.journals.plos import PLOS
from src.types import SearchResultsDF


def _run(journal: Nature | PLOS) -> DataFrame:
    data: List[DataFrame] = []
    products: List[Tuple[str, int]] = list(
        product(
            SEARCH_KEYWORDS["keyword"].tolist(),
            YEARS["year"].tolist(),
        )
    )

    pair: Tuple[str, int]
    for pair in products:
        df: DataFrame = journal.searchJournal(query=pair[0], year=pair[1])
        data.append(df)

    df: DataFrame = pandas.concat(objs=data, ignore_index=True)

    SearchResultsDF(df_dict=df.to_dict(orient="records"))

    return df


def nature() -> DataFrame:
    return _run(journal=Nature())


def plos() -> DataFrame:
    return _run(journal=PLOS())
