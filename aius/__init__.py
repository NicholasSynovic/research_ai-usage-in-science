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
        "tag": ["uses_dl", "uses_ptms", "identify_ptms"],
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
            text(
                md="""
## (C) Context:

You are an AI model integrated into an automated pipeline that processes academic Computational Natural Science papers into a machine-readable format. Your sole responsibility is to evaluate the paper's content and determine what pre-trained deep learning models the authors use in their methodology. Your response will be consumed by downstream systems that require structured JSON.
Pre-trained deep learning models have many different names. The following is a list of pre-trained deep learning model names and their data modality that you can refence in your analysis:

```json
{
    "text_models": ["ALBERT", "Apertus", "Arcee", "Bamba", "BART", "BARThez", "BARTpho", "BERT", "BertGeneration", "BertJapanese", "BERTweet", "BigBird", "BigBirdPegasus", "BioGpt", "BitNet", "Blenderbot", "Blenderbot Small", "BLOOM", "BLT", "BORT", "ByT5", "CamemBERT", "CANINE", "CodeGen", "CodeLlama", "Cohere", "Cohere2", "ConvBERT", "CPM", "CPMANT", "CTRL", "DBRX", "DeBERTa", "DeBERTa-v2", "DeepSeek-V2", "DeepSeek-V3", "DialoGPT", "DiffLlama", "DistilBERT", "Doge", "dots1", "DPR", "ELECTRA", "Encoder Decoder Models", "ERNIE", "Ernie4_5", "Ernie4_5_MoE", "ErnieM", "ESM", "EXAONE-4.0", "Falcon", "Falcon3", "FalconH1", "FalconMamba", "FLAN-T5", "FLAN-UL2", "FlauBERT", "FlexOlmo", "FNet", "FSMT", "Funnel Transformer", "Fuyu", "Gemma", "Gemma2", "GLM", "glm4", "glm4_moe", "GPT", "GPT Neo", "GPT NeoX", "GPT NeoX Japanese", "GPT-J", "GPT2", "GPTBigCode", "GptOss", "GPTSAN Japanese", "GPTSw3", "Granite", "GraniteMoe", "GraniteMoeHybrid", "GraniteMoeShared", "Helium", "HerBERT", "HGNet-V2", "HunYuanDenseV1", "HunYuanMoEV1", "I-BERT", "Jamba", "JetMoe", "Jukebox", "LED", "LFM2", "LLaMA", "Llama2", "Llama3", "LongCatFlash", "Longformer", "LongT5", "LUKE", "M2M100", "MADLAD-400", "Mamba", "Mamba2", "MarianMT", "MarkupLM", "MBart and MBart-50", "MEGA", "MegatronBERT", "MegatronGPT2", "MiniMax", "Ministral", "Mistral", "Mixtral", "mLUKE", "MobileBERT", "ModernBert", "ModernBERTDecoder", "MPNet", "MPT", "MRA", "MT5", "MVP", "myt5", "Nemotron", "NEZHA", "NLLB", "NLLB-MoE", "Nyströmformer", "OLMo", "OLMo2", "Olmo3", "OLMoE", "Open-Llama", "OPT", "Pegasus", "PEGASUS-X", "Persimmon", "Phi", "Phi-3", "PhiMoE", "PhoBERT", "PLBart", "ProphetNet", "QDQBert", "Qwen2", "Qwen2MoE", "Qwen3", "Qwen3MoE", "Qwen3Next", "RAG", "REALM", "RecurrentGemma", "Reformer", "RemBERT", "RetriBERT", "RoBERTa", "RoBERTa-PreLayerNorm", "RoCBert", "RoFormer", "RWKV", "Seed-Oss", "Splinter", "SqueezeBERT", "StableLm", "Starcoder2", "SwitchTransformers", "T5", "T5Gemma", "T5v1.1", "TAPEX", "Transformer XL", "UL2", "UMT5", "VaultGemma", "X-MOD", "XGLM", "XLM", "XLM-ProphetNet", "XLM-RoBERTa", "XLM-RoBERTa-XL", "XLM-V", "XLNet", "xLSTM", "YOSO", "Zamba", "Zamba2"],
    "vision_models": ["Aimv2", "BEiT", "BiT", "Conditional DETR", "ConvNeXT", "ConvNeXTV2", "CvT", "D-FINE", "DAB-DETR", "Deformable DETR", "DeiT", "Depth Anything", "Depth Anything V2", "DepthPro", "DETA", "DETR", "DiNAT", "DINOV2", "DINOv2 with Registers", "DINOv3", "DiT", "DPT", "EfficientFormer", "EfficientLoFTR", "EfficientNet", "EoMT", "FocalNet", "GLPN", "HGNet-V2", "Hiera", "I-JEPA", "ImageGPT", "LeViT", "LightGlue", "Mask2Former", "MaskFormer", "MLCD", "MobileNetV1", "MobileNetV2", "MobileViT", "MobileViTV2", "NAT", "PoolFormer", "Prompt Depth Anything", "Pyramid Vision Transformer (PVT)", "Pyramid Vision Transformer v2 (PVTv2)", "RegNet", "ResNet", "RT-DETR", "RT-DETRv2", "SAM2", "SegFormer", "SegGpt", "Segment Anything", "Segment Anything High Quality", "SuperGlue", "SuperPoint", "SwiftFormer", "Swin Transformer", "Swin Transformer V2", "Swin2SR", "Table Transformer", "TextNet", "Timm Wrapper", "UperNet", "VAN", "Vision Transformer (ViT)", "ViT Hybrid", "ViTDet", "ViTMAE", "ViTMatte", "ViTMSN", "ViTPose", "YOLOS", "ZoeDepth"],
    "audio_models": ["Audio Spectrogram Transformer", "Bark", "CLAP", "CSM", "dac", "Dia", "EnCodec", "FastSpeech2Conformer", "GraniteSpeech", "Hubert", "Kyutai Speech-To-Text", "MCTCT", "Mimi", "MMS", "Moonshine", "Moshi", "MusicGen", "MusicGen Melody", "Parakeet", "Pop2Piano", "Seamless-M4T", "SeamlessM4T-v2", "SEW", "SEW-D", "Speech2Text", "Speech2Text2", "SpeechT5", "UniSpeech", "UniSpeech-SAT", "UnivNet", "VITS", "Wav2Vec2", "Wav2Vec2-BERT", "Wav2Vec2-Conformer", "Wav2Vec2Phoneme", "WavLM", "Whisper", "X-Codec", "XLS-R", "XLSR-Wav2Vec2"],
    "video_models": ["SAM2 Video", "TimeSformer", "V-JEPA 2", "VideoMAE", "ViViT"],
    "multimodal_models": ["ALIGN", "AltCLIP", "Aria", "AyaVision", "BLIP", "BLIP-2", "BridgeTower", "BROS", "Chameleon", "Chinese-CLIP", "CLIP", "CLIPSeg", "CLVP", "Cohere2Vision", "ColPali", "ColQwen2", "Data2Vec", "DeepseekVL", "DeepseekVLHybrid", "DePlot", "Donut", "EdgeTAM", "EdgeTamVideo", "Emu3", "Evolla", "FLAVA", "Florence2", "Gemma3", "Gemma3n", "GIT", "glm4v", "glm4v_moe", "GOT-OCR2", "GraniteVision", "Grounding", "DINO", "GroupViT", "IDEFICS", "Idefics2", "Idefics3", "InstructBLIP", "InstructBlipVideo", "InternVL", "Janus", "KOSMOS-2", "KOSMOS-2.5", "LayoutLM", "LayoutLMV2", "LayoutLMV3", "LayoutXLM", "LFM2-VL", "LiLT", "Llama4", "LLaVA", "LLaVA-NeXT", "LLaVa-NeXT-Video", "LLaVA-Onevision", "LXMERT", "MatCha", "MetaCLIP 2", "MGP-STR", "Mistral3", "mllama", "MM Grounding DINO", "Nougat", "OmDet-Turbo", "OneFormer", "Ovis2", "OWL-ViT", "OWLv2", "PaliGemma", "Perceiver", "PerceptionLM", "Phi4", "Multimodal", "Pix2Struct", "Pixtral", "Qwen2.5-Omni", "Qwen2.5-VL", "Qwen2Audio", "Qwen2VL", "Qwen3-Omni-MoE", "Qwen3VL", "Qwen3VLMoe", "ShieldGemma2", "SigLIP", "SigLIP2", "SmolLM3", "SmolVLM", "Speech Encoder Decoder Models", "TAPAS", "TrOCR", "TVLT", "TVP", "UDOP", "VideoLlava", "ViLT", "VipLlava", "Vision Encoder Decoder Models", "Vision Text Dual Encoder", "VisualBERT", "Voxtral", "X-CLIP"]
    "reinforcement_learning_models": ["Decision Transformer", "Trajectory Transformer"],
    "time_series_models": ["Autoformer", "Informer", "PatchTSMixer", "PatchTST", "Time Series Transformer", "TimesFM"],
    "graph_models": ["Graphormer"]
}
```

However, not all papers use these models. In the event that the paper does not use one of these PTMs, identify the PTM.

## (O) Objective:
Your task is to output only an array of JSON objects containing key-value pairs, where:

- the key "model" value is a string of the pre-trained deep learning models name as stated in the prose, and
- the key "prose" value is the most salient excerpt from the paper that shows concrete evidence of the pre-trained model's usage.

No explanations or extra output are allowed.

## (S) Style:

Responses must be strictly machine-readable JSON. No natural language, commentary, or formatting beyond the JSON object is permitted.

## (T) Tone:

Neutral, objective, and machine-like.

## (A) Audience:

The audience is a machine system that parses JSON. Human readability is irrelevant.

## (R) Response:

Return only an array of JSON objects of the form:

```json
[
    {
        "model": "string",
        "prose": "string",
    },

    ...

]
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
