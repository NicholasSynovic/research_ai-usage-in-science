import json

import pandas
from pandas import DataFrame, Series

import aius
from aius.db import DB


def get_papers_openalex_data(db: DB) -> DataFrame:
    # Get papers that are open access and have at least 1 citation
    sql: str = """
        SELECT openalex.*, papers.doi FROM openalex
        JOIN papers ON openalex.paper_id = papers._id
        WHERE json_extract(openalex.json, '$.primary_location.is_oa') = 1
        AND openalex.cited_by_count > 0;
    """

    return pandas.read_sql_query(sql=sql, con=db.engine, index_col="_id")


def apply_filters(data_df: DataFrame) -> DataFrame:
    # Filter for at least two topics
    mask = (
        data_df.apply(
            lambda row: row.isin(aius.FIELD_FILTER).sum(),
            axis=1,
        )
        >= 2
    )
    filtered_on_topics: DataFrame = data_df[mask]

    # Cleanup data
    filtered_on_topics = filtered_on_topics.sort_values(by="paper_id")
    filtered_on_topics = filtered_on_topics.reset_index(drop=True)

    return filtered_on_topics
