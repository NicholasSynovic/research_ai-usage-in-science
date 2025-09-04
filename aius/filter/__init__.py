import pandas
from pandas import DataFrame

import aius
from aius.db import DB


def get_papers_openalex_data(db: DB) -> DataFrame:
    sql: str = "SELECT openalex.*, papers.doi FROM openalex JOIN papers ON openalex.paper_id = papers._id;"

    return pandas.read_sql_query(sql=sql, con=db.engine, index_col="_id")


def apply_filters(data_df: DataFrame) -> DataFrame:
    # Filter for documents with more than 0 citations
    filtered_on_citations: DataFrame = data_df[data_df["cited_by_count"] > 0]

    # Filter for at least two topics
    mask = (
        filtered_on_citations.apply(
            lambda row: row.isin(aius.FIELD_FILTER).sum(),
            axis=1,
        )
        >= 2
    )
    filtered_on_topics: DataFrame = filtered_on_citations[mask]

    # Cleanup data
    filtered_on_topics = filtered_on_topics.sort_values(by="paper_id")
    filtered_on_topics = filtered_on_topics.reset_index(drop=True)

    return filtered_on_topics
