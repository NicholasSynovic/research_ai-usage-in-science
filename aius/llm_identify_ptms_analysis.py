import itertools
from math import ceil
from pathlib import Path

import pandas
from pandas import DataFrame, Series
from progress.bar import Bar
from requests import Response, post

import aius
from aius.db import DB


class LLMIdentifyPTMs:
    def __init__(
        self,
        db: DB,
        model: str,
        uses_ptms_df: DataFrame,
        ollama_uri: str = "localhost:11434",
        index: int = 0,
        stride: int = 1,
    ) -> None:
        # Global variables
        self.index: int = index
        self.stride: int = stride
        self.model: str = model.replace("'", "").replace('"', "")
        self.ollama_uri: str = f"http://{ollama_uri}/api/generate"

        # Set output path to the file
        self.output_path: Path = Path(
            f"{model.replace(':', '-')}_identify_ptms_index-{self.index}_stride-{self.stride}.parquet"
        ).resolve()

        # Get prompt from the database
        prompts_df: DataFrame = pandas.read_sql_table(
            table_name="llm_prompts",
            con=db.engine,
        )
        self.prompt_tag: str = "identify_ptms"
        self.prompt: str = prompts_df[prompts_df["tag"] == self.prompt_tag][
            "prompt"
        ].reset_index(drop=True)[0]

        # Get prompt engineering papers
        # TODO: Modify this SQL to grab all NS paper content
        prompt_engineering_paper_query: str = """
        SELECT source.*, pnspc.formatted_md, pnspc.formatted_md_token_count
        FROM plos_natural_science_papers source
        JOIN plos_natural_science_paper_content pnspc
        ON pnspc.plos_paper_id = source.plos_paper_id;
        """
        papers: DataFrame = pandas.read_sql_query(
            sql=prompt_engineering_paper_query, con=db.engine, index_col="_id"
        )

        self.papers: DataFrame = uses_ptms_df.join(other=papers)
        self.papers = self.papers.drop(columns=["result", "prose"])

        self.paper_count: int = ceil(self.papers.shape[0] / self.stride)

        # Get the max number of tokens to instantiate the model to use
        self.max_tokens: int = (
            int(self.papers["formatted_md_token_count"].max()) + 10000
        )

    def run(self) -> None:
        # Data structure to store model responses
        data: dict[str, list] = {
            "model": [],
            "response_text": [],
            "system_prompt_tag": [],
            "plos_prompt_enineering_paper_id": [],
        }

        # JSON body to send in POST request
        json_data: dict = {
            "model": self.model,
            "stream": False,
            "prompt": "",  # Change me in the `for` loop
            "system": self.prompt,
            "keep_alive": "30m",
            "options": {
                "temperature": 0.1,
                "top_k": 1,
                "top_p": 0.1,
                "num_predict": 1000,
                "num_ctx": self.max_tokens,
                "seed": 42,
            },
        }

        iterator: itertools.islice = itertools.islice(
            self.papers.iterrows(),
            self.index,
            None,
            self.stride,
        )

        with Bar(
            f"Analyzing papers with {self.model} on {self.prompt_tag}...",
            max=self.paper_count,
        ) as bar:
            row: Series
            for idx, row in iterator:
                data["model"].append(self.model)
                data["system_prompt_tag"].append(self.prompt_tag)
                data["plos_prompt_enineering_paper_id"].append(idx)

                json_data["prompt"] = row["formatted_md"]
                resp: Response = post(
                    url=self.ollama_uri,
                    timeout=aius.POST_TIMEOUT,
                    json=json_data,
                )

                data["response_text"].append(resp.content.decode())

                bar.next()

        DataFrame(data=data).to_parquet(path=self.output_path, engine="pyarrow")
