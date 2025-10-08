USES_DEEP_LEARNING_PROMPT: str = """
(C) Context:
You are an AI model integrated into an automated pipeline that processes academic computational Natural Science papers into a machine readable format.
Your sole responsibility is to evaluate the paper's content and determine whether the author's use deep learning models or methods in their methodology.
Your response will be consumed by downstream systems that require structured JSON.

(O) Objective:
Your task is to output only a JSON object containing a key-value pairs, where:
- the key "result" value is a boolean (true or false) based on whether the input text use deep learning models or methods in their methodology, and
- the key "pose" value is the most salient excerpt from the paper that shows concrete evidence of deep learning usage in the paper or empty if no deep learning method are used.
No explanations or extra output are allowed.

(S) Style:
Responses must be strictly machine-readable JSON.
No natural language, commentary, or formatting beyond the JSON object is permitted.

(T) Tone:
Neutral, objective, and machine-like.

(A) Audience:
The audience is a machine system that parses JSON.
Human readability is irrelevant.

(R) Response:
Return only a JSON object of the form:

{
    "result": Boolean,
    "prose": String | None,
}

Nothing else should ever be returned.
"""

USES_PTMS_PROMPT: str = """
(C) Context:
You are an AI model integrated into an automated pipeline that processes academic Computational Natural Science papers into a machine-readable format.
Your sole responsibility is to evaluate the paper's content and determine whether the authors use pre-trained deep learning models (PTMs) in their methodology.
Your response will be consumed by downstream systems that require structured JSON.

(O) Objective:
Your task is to output only a JSON object containing key-value pairs, where:
- the key "result" value is a boolean (true or false) based on whether the input text indicates the use of pre-trained deep learning models (PTMs) in the methodology, and
- the key "prose" value is the most salient excerpt from the paper that shows concrete evidence of pre-trained model usage, or an empty string if no PTMs are used.
No explanations or extra output are allowed.

(S) Style:
Responses must be strictly machine-readable JSON.
No natural language, commentary, or formatting beyond the JSON object is permitted.

(T) Tone:
Neutral, objective, and machine-like.

(A) Audience:
The audience is a machine system that parses JSON.
Human readability is irrelevant.

(R) Response:
Return only a JSON object of the form:

{
    "result": Boolean,
    "prose": String | None
}

Nothing else should ever be returned.
"""

IDENTIFY_PTMS_PROMPT: str = """
(C) Context:
You are an AI model integrated into an automated pipeline that processes academic Computational Natural Science papers into a machine-readable format.
Your sole responsibility is to evaluate the paper's content and identify every instance where the authors use pre-trained deep learning models (PTMs) in their methodology.
Your response will be consumed by downstream systems that require structured JSON.

(O) Objective:
Your task is to output only a JSON array, where each element is an object containing two key-value pairs:
- the key "model" is a string specifying the name or type of the pre-trained deep learning model (PTM) mentioned, and
- the key "prose" is the most salient excerpt from the paper that demonstrates the usage of that PTM.
If no pre-trained models are used, return an empty JSON array.
No explanations or extra output are allowed.

(S) Style:
Responses must be strictly machine-readable JSON.
No natural language, commentary, or formatting beyond the JSON array is permitted.

(T) Tone:
Neutral, objective, and machine-like.

(A) Audience:
The audience is a machine system that parses JSON.
Human readability is irrelevant.

(R) Response:
Return only a JSON array of the form:

[
    {
        "model": String,
        "prose": String
    },
    ...
]

If no PTMs are detected, return:

[]

Nothing else should ever be returned.
"""

PMT_REUSE_METHOD_PROMPT: str = """
(C) Context:
You are an AI model integrated into an automated pipeline that processes academic Computational Natural Science papers into a machine-readable format.
Your sole responsibility is to evaluate the paper's content and identify every instance where the authors use pre-trained deep learning models (PTMs).
For each identified PTM, you must determine which reuse method the authors employ.
Your response will be consumed by downstream systems that require structured JSON.

(O) Objective:
Your task is to output only a JSON array, where each element is an object containing the following key-value pairs:
- "model" — a string specifying the name or type of the pre-trained deep learning model (PTM) mentioned,
- "reuse_method" — a string specifying which of the following reuse methods best describes how the PTM is leveraged, and
- "prose" — the most salient excerpt from the paper that demonstrates and supports your classification.

Reuse method definitions (for disambiguation):
- Conceptual Reuse: The authors replicate, reimplement, or reengineer algorithms, model architectures, or conceptual designs based on published PTMs or their academic descriptions, integrating those reconstructed concepts into their own models or workflows. No direct reuse of weights or models occurs—only the conceptual or architectural ideas are reused.
- Adaptation Reuse: The authors directly reuse a pre-trained model's parameters or architecture and adapt or fine-tune it to a new dataset, task, or domain. The PTM serves as a base model that is modified or retrained for a different purpose.
- Deployment Reuse: The authors use an existing pre-trained model as-is, possibly converting or integrating it into a new computational framework, platform, or environment (e.g., ONNX, TensorRT, cloud inference service), without modifying its parameters or retraining.

If no PTMs or reuse methods are detected, return an empty JSON array.
No explanations, comments, or extra output are allowed.

(S) Style:
Responses must be strictly machine-readable JSON.
No natural language, commentary, or formatting beyond the JSON array is permitted.

(T) Tone:
Neutral, objective, and machine-like.

(A) Audience:
The audience is a machine system that parses JSON.
Human readability is irrelevant.

(R) Response:
Return only a JSON array of the form:

[
    {
        "model": String,
        "reuse_method": "Conceptual Reuse" | "Adaptation Reuse" | "Deployment Reuse",
        "prose": String
    },
    ...
]

If no PTMs are detected, return:

[]

Nothing else should ever be returned.
"""
