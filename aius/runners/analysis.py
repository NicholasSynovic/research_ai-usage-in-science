from json import dumps, loads
from logging import Logger

import pandas
from openai import OpenAI, InternalServerError
from openai.types.chat.chat_completion import ChatCompletion
from pandas import DataFrame, Series
from progress.bar import Bar

from aius.db import DB
from aius.runners.runner import Runner


class AnalysisRunner(Runner):
    def __init__(
        self,
        logger: Logger,
        db: DB,
        prompt_id: str,
        alcf_auth_token: str,
    ) -> None:
        # Set class constants
        self.logger: Logger = logger
        self.db: DB = db
        self.prompt_id: str = prompt_id

        self.openai_client: OpenAI = OpenAI(
            api_key=alcf_auth_token,
            base_url="https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1",
        )
        self.model: str = "openai/gpt-oss-120b"

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
            for _, row in df.iterrows():
                data["doi"].append(row["doi"])
                user_prompt: str = row["markdown"]

                try:
                    resp: ChatCompletion = self.inference(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                    )
                except InternalServerError:
                    bar.next()
                    continue

                data["response"].append(
                    dumps(
                        obj=loads(s=resp.choices[0].message.content),
                        indent=4,
                    )
                )

                data["reasoning"].append(resp.choices[0].message.reasoning_content)

                bar.next()

        self._write_data_to_table(
            data=DataFrame(data=data), table=f"{self.prompt_id}_analysis"
        )
        return 0
