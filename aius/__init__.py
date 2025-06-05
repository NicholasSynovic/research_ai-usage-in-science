from pandas import DataFrame

YEARS: DataFrame = DataFrame(data={"year": list(range(2014, 2025))})

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

JOURNALS: DataFrame = DataFrame(
    data={"journal": ["Nature", "PLOS", "Science"]}
)
