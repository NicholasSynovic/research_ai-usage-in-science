"""
LLM inference runner.

Copyright 2025 (C) Nicholas M. Synovic

"""

from json import dumps, loads
from logging import Logger

import pandas as pd
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from pandas import DataFrame, Series
from progress.bar import Bar
from pydantic import BaseModel

from aius.db import DB
from aius.runners.runner import Runner


class UsesDL_Model(BaseModel):  # noqa: D101, N801
    doi: str
    uses_dl: bool = False
    reasoning: str = ""


class AnalysisRunner(Runner):  # noqa: D101
    def __init__(  # noqa: D107
        self,
        logger: Logger,
        db: DB,
        prompt_id: str,
        alcf_auth_token: str,
    ) -> None:
        self.logger: Logger = logger
        self.db: DB = db
        self.prompt_id: str = prompt_id

        self.openai_client: OpenAI = OpenAI(
            api_key=alcf_auth_token,
            base_url="https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1",
        )
        self.model: str = "openai/gpt-oss-20b"

    def get_prompt(self) -> str:  # noqa: D102
        df: DataFrame = pd.read_sql_table(
            table_name="_llm_prompts",
            con=self.db.engine,
            index_col="_id",
        )

        prompt_df: DataFrame = df[df["tag"] == self.prompt_id].reset_index(drop=True)

        return prompt_df["prompt"][0]

    def get_data(self) -> DataFrame:  # noqa: D102
        match self.prompt_id:
            case "uses_dl":
                return pd.read_sql_table(
                    table_name="markdown",
                    con=self.db.engine,
                    index_col="_id",
                )
            case "uses_ptms":
                return pd.read_sql_table(
                    table_name="uses_dl_analysis",
                    con=self.db.engine,
                    index_col="_id",
                )

        return DataFrame()

    def inference(  # noqa: D102
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> ChatCompletion:
        return self.openai_client.chat.completions.create(
            model=self.model,
            reasoning_effort="high",
            frequency_penalty=0,
            stream=False,
            seed=42,
            n=1,
            temperature=0.1,
            top_p=0.1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

    def execute(self) -> int:  # noqa: D102
        data: dict[str, list[str]] = {
            "doi": [],
            "response": [],
            "reasoning": [],
        }

        system_prompt: str = self.get_prompt()
        df: DataFrame = self.get_data()

        with Bar(
            f"Inferencing with {self.model} on {self.prompt_id} system prompt...",
            max=df.shape[0],
        ) as bar:
            row: Series
            for _, row in df.iterrows():
                user_prompt: str = row["markdown"]

                try:
                    resp: ChatCompletion = self.inference(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                    )
                except Exception:  # noqa: BLE001
                    bar.next()
                    continue

                data["doi"].append(row["doi"])
                data["reasoning"].append(resp.choices[0].message.reasoning_content)
                data["response"].append(
                    dumps(
                        obj=loads(s=resp.choices[0].message.content),
                        indent=4,
                    )
                )

                bar.next()

        self.db.write_dataframe_to_table(
            df=DataFrame(data=data), table_name=f"{self.prompt_id}_analysis"
        )
        return 0
