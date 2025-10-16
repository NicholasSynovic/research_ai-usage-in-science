from pathlib import Path
from typing import Literal

import pandas
from pandas import DataFrame, Series
from progress.bar import Bar
from requests import Response, post

import aius
from aius.db import DB


class LLMPromptEngineering:
    def __init__(
        self,
        db: DB,
        prompt_tag: str,
        model: str,
        ollama_uri: str = "localhost:11434",
        dataset_size: Literal["small", "large"] = "small",
    ) -> None:
        # DB connection
        self.db: DB = db

        # Ensure proper naming of the Ollama model
        self.model: str = model.replace("'", "").replace('"', "")

        # Create Ollama API endpoint
        self.ollama_uri: str = f"http://{ollama_uri}/api/generate"

        # Resolve path to output parquet file
        self.output_path: Path = Path(
            f"{model.replace(':', '-')}_{prompt_tag}.parquet"
        ).resolve()

        # LLM prompt tag and prompt
        self.prompt_tag: str = prompt_tag.lower()
        self.prompt = self.get_prompt_from_db()

        # Get the paper content, number of papers, and maximum tokens of the
        # content from the database given the dataset size
        self.papers: DataFrame
        self.paper_count: int
        self.max_tokens: int
        self.papers, self.paper_count, self.max_tokens = self.get_paper_content(
            dataset_size=dataset_size,
        )

        # Run the analysis and save to an output file
        self.run()

    def get_prompt_from_db(self) -> str:
        # Get prompt from the database
        prompts_df: DataFrame = pandas.read_sql_table(
            table_name="llm_prompts",
            con=self.db.engine,
        )

        return prompts_df[prompts_df["tag"] == self.prompt_tag]["prompt"].reset_index(
            drop=True
        )[0]

    def get_paper_content(
        self,
        dataset_size: Literal["small", "large"],
    ) -> tuple[DataFrame, int, int]:
        # Identify which table to source `plos_paper_id` from
        table_name: str
        match dataset_size:
            case "small":
                table_name = "plos_llm_prompt_engineering_papers"
            case "large":
                table_name = "plos_author_agreement_papers"

        # Query to get the necessary data
        db_query: str = f"""
        SELECT
            source.*,
            pnspc.formatted_md,
            pnspc.formatted_md_token_count
        FROM
            {table_name} source
        JOIN
            plos_natural_science_paper_content pnspc
        ON
            pnspc.plos_paper_id = source.plos_paper_id;
        """

        # Get the papers from the database
        df: DataFrame = pandas.read_sql_query(
            sql=db_query,
            con=self.db.engine,
        )

        # Count the total number of papers returned
        paper_count: int = df.shape[0]

        # Get the max number of tokens to instantiate the model to use
        max_tokens: int = int(df["formatted_md_token_count"].max()) + 10000

        return (df, paper_count, max_tokens)

    def run(self) -> DataFrame:
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

        with Bar(
            f"Analyzing papers with {self.model} on {self.prompt_tag}...",
            max=self.paper_count,
        ) as bar:
            row: Series
            for _, row in self.papers.iterrows():
                data["model"].append(self.model)
                data["system_prompt_tag"].append(self.prompt_tag)
                data["plos_prompt_enineering_paper_id"].append(row["_id"])

                json_data["prompt"] = row["formatted_md"]
                resp: Response = post(
                    url=self.ollama_uri,
                    timeout=aius.POST_TIMEOUT,
                    json=json_data,
                )

                data["response_text"].append(resp.content.decode())

                bar.next()

        DataFrame(data=data).to_parquet(path=self.output_path, engine="pyarrow")
