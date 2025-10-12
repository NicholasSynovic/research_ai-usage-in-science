"""
Global variables for `aius`.

Copyright 2025 (C) Nicholas M. Synovic

"""

from mdformat import text
from pandas import DataFrame

MODULE_NAME: str = "aius"
PROGRAM_NAME: str = "AIUS"
PROGRAM_DESCRIPTION: str = "Identify AI usage in Natural Science research papers"
PROGRAM_EPILOG: str = "Copyright 2025 (C) Nicholas M. Synovic"
JOURNALS: DataFrame = DataFrame(data={"journal": ["Nature", "PLOS", "Science"]})
GET_TIMEOUT: int = 60
POST_TIMEOUT: int = 60
YEAR_LIST: list[int] = list(range(2014, 2025))
YEARS: DataFrame = DataFrame(data={"year": YEAR_LIST})

FIELD_FILTER: set[str] = {
    "Agricultural and Biological Sciences",
    "Environmental Science",
    "Biochemistry Genetics and Molecular Biology",
    "Immunology and Microbiology",
    "Neuroscience",
    "Earth and Planetary Sciences",
    "Physics and Astronomy",
    "Chemistry",
}

KEYWORD_LIST: list[str] = [
    r'"Deep Learning"',
    r'"Deep Neural Network"',
    r'"Hugging Face"',
    r'"HuggingFace"',
    r'"Model Checkpoint"',
    r'"Model Weights"',
    r'"Pre-Trained Model"',
]


SEARCH_KEYWORDS: DataFrame = DataFrame(
    data={
        "keyword": [
            r'"Deep Learning"',
            r'"Deep Neural Network"',
            r'"Hugging Face"',
            r'"HuggingFace"',
            r'"Model Checkpoint"',
            r'"Model Weights"',
            r'"Pre-Trained Model"',
        ]
    }
)

LLM_PROMPTS: DataFrame = DataFrame(
    data={
        "tag": ["uses_dl"],
        "prompt": [
            text(
                md="""
## (C) Context
You are an AI model integrated into an automated pipeline that processes academic computational Natural Science papers into a machine readable format. Your sole responsibility is to evaluate the paper's content and determine whether the author's use deep learning models or methods in their methodology. Your response will be consumed by downstream systems that require structured JSON.

## (O) Objective
Your task is to output only a JSON object containing a key-value pairs, where:

- the key "result" value is a boolean (true or false) based on whether the input text use deep learning models or methods in their methodology, and
- the key "pose" value is the most salient excerpt from the paper that shows concrete evidence of deep learning usage in the paper or empty if no deep learning method are used.

No explanations or extra output are allowed.

## (S) Style
Responses must be strictly machine-readable JSON. No natural language, commentary, or formatting beyond the JSON object is permitted.

## (T) Tone
Neutral, objective, and machine-like.

## (A) Audience
The audience is a machine system that parses JSON. Human readability is irrelevant.

## (R) Response
Return only a JSON object of the form:

```json
{
    "result": "boolean",
    "prose": "string" | None,
}
```

Nothing else should ever be returned.
"""
            ),
        ],
    }
)
