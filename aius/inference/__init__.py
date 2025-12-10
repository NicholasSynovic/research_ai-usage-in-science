# from abc import ABC, abstractmethod

# from openai.types.chat import ChatCompletion

# from aius.inference.models import Document, ModelResponse, UsesDL
from aius.inference.prompts import *

SYSTEM_PROMPT_TAG_MAPPING: dict[str, COSTAR_SystemPrompt] = {
    "uses_dl": USES_DL_PROMPT,
    "uses_ptms": USES_PTMS_PROMPT,
    "identify_ptms": IDENTIFY_PTMS_PROMPT,
    "identify_ptm_reuse": IDENTIFY_PTM_REUSE_PROMPT,
    "identify_ptm_impact": IDENTIFY_PTM_IMPACT_IN_SCIENTIFIC_PROCESS,
}


# class Inference(ABC):
#     def __init__(self) -> None:
#         pass

#     @abstractmethod
#     def inference_document(
#         self,
#         system_prompt: str,
#         document: Document,
#     ) -> ChatCompletion: ...

#     @abstractmethod
#     def inference_documents(
#         self,
#         system_prompt: str,
#         documents: list[Document],
#     ) -> list[ModelResponse]: ...

#     @abstractmethod
#     def parse_uses_dl(self, responses: list[ModelResponse]) -> list[UsesDL]: ...
