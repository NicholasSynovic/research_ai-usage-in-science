"""
Filter for Natural Science PLOS documents.

Copyright 2025 (C) Nicholas M. Synovic

"""

import pandas as pd
from pandas import DataFrame

import aius
from aius.db import DB


class NaturalScienceFilter:
    def __init__(self, db: DB) -> None:
        # SQLite3 query for OpenAlex metadata and where documents are both
        # open_access and cited_by_count > 0
        sql_query: str = """
            SELECT ppom.plos_paper_id, ppom.topic_0, ppom.topic_1, ppom.topic_2
            FROM plos_paper_openalex_metadata AS ppom
            WHERE ppom.open_access = 1
            AND ppom.cited_by_count > 0;
        """

        # Execute SQL query
        self.df: DataFrame = pd.read_sql_query(sql=sql_query, con=db.engine)

        # Create mask selecting rows that have at least two Natural Science
        # fields
        mask = (
            self.df.apply(
                lambda row: row.isin(aius.FIELD_FILTER).sum(),
                axis=1,
            )
            >= 2
        )

        # Apply mask
        self.df = (
            self.df[mask]
            .reset_index(drop=True)
            .drop(
                columns=["topic_0", "topic_1", "topic_2"],
            )
        )
