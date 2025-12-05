import mdformat
from pydantic import BaseModel


class COSTAR_SystemPrompt(BaseModel):  # noqa: D101, N801
    tag: str
    context: str
    objective: str
    response: str
    style: str = "Responses must be strictly machine-readable JSON. No natural language, commentary, or formatting beyond the JSON object is permitted."  # noqa: E501
    tone: str = "Neutral, objective, and machine-like."
    audience: str = "The audience is a machine system that parses JSON. Human readability is irrelevant."  # noqa: E501

    def create_prompt(self) -> str:  # noqa: D102
        return mdformat.text(
            options={"wrap": 80},
            md=f"""
## Context:
{self.context}

## Objective
{self.objective}

## Style
{self.style}

## Tone
{self.tone}

## Audience
{self.audience}

## Response
{self.response}
""",
        )


class Document(BaseModel):
    doi: str
    content: str


class ModelResponse(BaseModel):
    doi: str
    system_prompt: str
    user_prompt: str
    model_response: str
    model_reasoning: str
    compute_time_seconds: str


class UsesDL(BaseModel):
    doi: str
    model_response: str
    model_reasoning: str
    uses_dl: str
    uses_dl_evidence: str
    compute_time_seconds: str
