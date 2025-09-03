from pandas import DataFrame
from progress.bar import Bar
from requests import Response, get

import aius


class OpenAlex:
    def __init__(self, email: str, papers_df: DataFrame) -> None:
        # Instantiate class variables
        self.email: str = email
        self.papers_df: DataFrame = papers_df

        # Create a list of DataFrame chunks to iterate through
        self.papers_df_list: list[DataFrame] = [
            self.papers_df[i : i + 25]
            for i in range(
                0,
                len(self.papers_df),
                25,
            )
        ]

    def get_metadata(self) -> DataFrame:
        # Get the maximum of the bar
        bar_max: int = len(self.papers_df_list)

        with Bar("Calling OpenAlex REST API... ", max=bar_max) as bar:
            # Iterate through the list of DataFrames
            df_chunk: DataFrame
            for df_chunk in self.papers_df_list:
                print(df_chunk)
                bar.next()

        return DataFrame()
