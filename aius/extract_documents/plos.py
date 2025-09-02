from json import loads

from pandas import DataFrame, Series
from progress.bar import Bar

from aius.extract_documents import JournalExtractor


class PLOS(JournalExtractor):
    def __init__(self) -> None:
        self.name = "plos"

    def extract_all_papers(self, search_data: DataFrame) -> DataFrame:
        search_data_size: int = search_data.shape[1]

        with Bar("Extracting papers...", max=search_data_size) as bar:
            row: Series
            for _, row in search_data.iterrows():
                for json_str in search_data:
                    json_data: dict = loads(s=json_str)
                    print(json_data)
                    break
                    bar.next()

        return DataFrame()
