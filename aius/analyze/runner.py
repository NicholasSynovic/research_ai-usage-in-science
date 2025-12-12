"""
LLM inference runner.

Copyright 2025 (C) Nicholas M. Synovic

"""

from itertools import islice
from logging import Logger
from typing import Literal

import pandas as pd
from pandas import DataFrame
from pydantic import BaseModel

from aius.analyze import BACKEND_MAPPING, Document, ModelResponse
from aius.analyze.backend import Backend
from aius.db import DB
from aius.runner import Runner


class UsesDL_Model(BaseModel):  # noqa: D101, N801
    doi: str
    uses_dl: bool
    reasoning: str


class AnalysisRunner(Runner):  # noqa: D101
    def __init__(  # noqa: D107, PLR0917, PLR0913
        self,
        db: DB,
        logger: Logger,
        system_prompt_id: str,
        model_name: str,
        index: int = 0,
        stride: int = 20,
        auth_key: str = "",
        backend_name: Literal["metis", "ollama", "sophia"] = "sophia",
        ollama_endpoint: str = "",
    ) -> None:
        super().__init__(name="analysis", db=db, logger=logger)

        self.stride: int = stride
        self.index: int = index
        self.ollama_endpoint: str = ollama_endpoint
        self.system_prompt_id: str = system_prompt_id.lower()

        self.backend: Backend = BACKEND_MAPPING[self.backend_name](
            name=backend_name, logger=self.logger
        )

        self.system_prompt: str = self._get_system_prompt()

    def _get_system_prompt(self) -> str:
        return self.db.get_llm_prompt(llm_prompt_id=self.system_prompt_id)

    def _get_documents(self) -> list[Document]:
        df: DataFrame = DataFrame()

        match self.system_prompt_id:
            case "uses_dl":
                df = self.db.read_table_to_dataframe(table_name="markdown")

        df_islice: islice = islice(
            df.iterrows(),
            self.index,
            None,
            self.stride,
        )

        return [
            Document(doi=row["doi"], content=row["markdown"]) for _, row in df_islice
        ]

    def execute(self) -> int:  # noqa: D102
        documents: list[Document] = self._get_documents()

        responses: list[ModelResponse] = self.backend.inference_documents(
            documents=documents,
            system_prompt=self.system_prompt,
        )

        df: DataFrame = pd.concat(
            objs=[resp.to_df for resp in responses],
            ignore_index=True,
        )

        df.to_parquet(
            path=f"aius_index-{self.index}_stride-{self.stride}.parquet",
            engine="pyarrow",
        )

        return 0
