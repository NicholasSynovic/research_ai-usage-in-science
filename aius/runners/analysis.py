from json import dumps, loads
from logging import Logger

import pandas
from openai import InternalServerError, OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from pandas import DataFrame, Series
from progress.bar import Bar
from pydantic import BaseModel

from aius.db import DB
from aius.runners import Runner


class UsesDL_Model(BaseModel):
    doi: str
    uses_dl: bool = False
    reasoning: str = ""


class AnalysisRunner(Runner):
    def __init__(
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

    def get_prompt(self) -> str:
        df: DataFrame = pandas.read_sql_table(
            table_name="_llm_prompts",
            con=self.db.engine,
            index_col="_id",
        )

        prompt_df: DataFrame = df[df["tag"] == self.prompt_id].reset_index(drop=True)

        return prompt_df["prompt"][0]

    def get_data(self) -> DataFrame:
        match self.prompt_id:
            case "uses_dl":
                return pandas.read_sql_table(
                    table_name="markdown",
                    con=self.db.engine,
                    index_col="_id",
                )
            case "uses_ptms":
                df: DataFrame = pandas.read_sql_table(
                    table_name="uses_dl_analysis",
                    con=self.db.engine,
                    index_col="_id",
                )

        return DataFrame()

    def inference(
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

    def _write_data_to_table(self, table: str, data: DataFrame) -> None:
        self.logger.info(msg=f"Writing data to the `{table}` table")
        self.logger.debug(msg=f"Data: {data}")
        data.to_sql(
            name=table,
            con=self.db.engine,
            if_exists="append",
            index=True,
            index_label="_id",
        )
        self.logger.info(msg=f"Wrote data to the `{table}` table")

    def execute(self) -> int:
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
            for _, row in df[0:100].iterrows():
                user_prompt: str = row["markdown"]

                try:
                    resp: ChatCompletion = self.inference(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                    )
                except InternalServerError:
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

        self._write_data_to_table(
            data=DataFrame(data=data), table=f"{self.prompt_id}_analysis"
        )
        return 0
