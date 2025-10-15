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
POST_TIMEOUT: int = 36000
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
        "tag": ["uses_dl", "uses_ptms"],
        "prompt": [
            text(
                md="""
## (C) Context
You are an AI model integrated into an automated pipeline that processes academic computational Natural Science papers into a machine readable format. Your sole responsibility is to evaluate the paper's content and determine whether the author's use deep learning models or methods in their methodology. Your response will be consumed by downstream systems that require structured JSON.

## (O) Objective
Your task is to output only a JSON object containing a key-value pairs, where:

- the key "result" value is a boolean (true or false) based on whether the input text use deep learning models or methods in their methodology, and
- the key "prose" value is the most salient excerpt from the paper that shows concrete evidence of deep learning usage in the paper or empty if no deep learning method are used.

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
            text(
                md="""
## (C) Context:

You are an AI model integrated into an automated pipeline that processes academic Computational Natural Science papers into a machine-readable format. Your sole responsibility is to evaluate the paper's content and determine whether the authors use pre-trained deep learning models (PTMs) in their methodology. Your response will be consumed by downstream systems that require structured JSON.

## (O) Objective:
Your task is to output only a JSON object containing key-value pairs, where:

- the key "result" value is a boolean (true or false) based on whether the input text indicates the use of pre-trained deep learning models (PTMs) in the methodology, and
- the key "prose" value is the most salient excerpt from the paper that shows concrete evidence of pre-trained model usage, or an empty string if no PTMs are used.

No explanations or extra output are allowed.

## (S) Style:

Responses must be strictly machine-readable JSON. No natural language, commentary, or formatting beyond the JSON object is permitted.

## (T) Tone:

Neutral, objective, and machine-like.

## (A) Audience:

The audience is a machine system that parses JSON. Human readability is irrelevant.

## (R) Response:

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

LLM_PROMPT_ENGINEERING_PAPERS: DataFrame = DataFrame(
    data={
        "doi": [
            "https://doi.org/10.1371/journal.pcbi.1010512",
            "https://doi.org/10.1371/journal.pcbi.1011818",
            "https://doi.org/10.1371/journal.pdig.0000536",
            "https://doi.org/10.1371/journal.pgen.1009436",
            "https://doi.org/10.1371/journal.pntd.0010937",
            "https://doi.org/10.1371/journal.pone.0086152",
            "https://doi.org/10.1371/journal.pone.0088597",
            "https://doi.org/10.1371/journal.pone.0093666",
            "https://doi.org/10.1371/journal.pone.0095718",
            "https://doi.org/10.1371/journal.pone.0096811",
            "https://doi.org/10.1371/journal.pone.0101765",
            "https://doi.org/10.1371/journal.pone.0103831",
            "https://doi.org/10.1371/journal.pone.0113159",
            "https://doi.org/10.1371/journal.pone.0114812",
            "https://doi.org/10.1371/journal.pone.0120570",
            "https://doi.org/10.1371/journal.pone.0185844",
            "https://doi.org/10.1371/journal.pone.0192011",
            "https://doi.org/10.1371/journal.pone.0196302",
            "https://doi.org/10.1371/journal.pone.0209649",
            "https://doi.org/10.1371/journal.pone.0217305",
        ]
    }
)
