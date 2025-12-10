"""
LLM inference runner.

Copyright 2025 (C) Nicholas M. Synovic

"""

from itertools import islice
from json import dumps, loads
from logging import Logger
from math import ceil
from typing import Literal

from openai.types.chat.chat_completion import ChatCompletion
from pandas import DataFrame, Series
from progress.bar import Bar
from pydantic import BaseModel

from aius.db import DB
from aius.inference.inference_backend import InferenceBackend
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
        system_prompt_id: str,
        index: int = 0,
        stride: int = 20,
        auth_key: str = "",
        backend: Literal["alcf", "ollama"] = "alcf",
        ollama_endpoint: str = "",
    ) -> None:
        super().__init__(name="analysis", db=db, logger=logger)

        self.stride: int = stride
        self.index: int = index
        self.endpoint: str = ollama_endpoint
        self.model_name: str = "gpt-oss:20b"

        if backend == "alcf":
            self.endpoint = (
                "https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1"
            )
            self.model_name: str = "openai/gpt-oss-20b"

        self.inference_backend: InferenceBackend = InferenceBackend(
            logger=self.logger,
            name="inference_backend",
            index=index,
            stride=stride,
            auth_key=auth_key,
            openai_endpoint=self.endpoint,
            model_name=self.model_name,
        )

        self.system_prompt_id: str = system_prompt_id.lower()
        self.system_prompt: str = self._get_system_prompt()

    def _get_system_prompt(self) -> str:
        return self.db.get_llm_prompt(llm_prompt_id=self.system_prompt_id)

    def _get_documents(self) -> tuple[islice, int]:
        df: DataFrame = DataFrame()

        match self.system_prompt_id:
            case "uses_dl":
                df = self.db.read_table_to_dataframe(table_name="markdown")

        row_count: int = ceil(df.shape[0] / self.stride)

        df_islice: islice = islice(
            df.iterrows(),
            self.index,
            None,
            self.stride,
        )

        return (df_islice, row_count)

    def execute(self) -> int:  # noqa: D102
        document_iterator: islice
        document_count: int
        document_iterator, document_count = self._get_documents()

        responses: DataFrame = self.inference_backend.inference_doucments(system_prompt=self.system_prompt,document_iterator=document_iterator, document_count=document_count,)

        self.db.write_dataframe_to_table(df=responses, table_name=f"{self.system_prompt_id}_analysis",)

        return 0
