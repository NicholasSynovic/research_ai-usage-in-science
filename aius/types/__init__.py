from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class SearchResultsDict(BaseModel):
    year: int = Field(ge=2014, lt=2025)
    query: Literal[
        r'"Deep Learning"',
        r'"Deep Neural Network"',
        r'"Hugging Face"',
        r'"HuggingFace"',
        r'"Model Checkpoint"',
        r'"Model Weights"',
        r'"Pre-Trained Model"',
    ]
    page: int = Field(ge=0)
    url: str
    status_code: int
    html: str | float
    count: Optional[int] = None
    journal: Literal["Nature", "PLOS", "Science"]


class SearchResultsDF(BaseModel):
    df_dict: List[SearchResultsDict]
