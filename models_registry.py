# models_registry.py

# Optimized 50+ Free Models Registry (51 unique models)
# Mapped by standard suitability for each task category

# 1. Orchestration & Brain Models (5 unique models)
ORCHESTRATOR_MODELS = [
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "qwen/qwen3-next-80b-a3b-instruct:free"
]

# 2. Coder / Programming Models (5 unique models)
CODER_MODELS = [
    "qwen/qwen3-coder:free",
    "cohere/north-mini-code:free",
    "poolside/laguna-m.1:free",
    "poolside/laguna-xs-2.1:free",
    "poolside/laguna-xs.2:free"
]

# 3. General Reasoning & Synthesis Models (10 unique models)
GENERAL_MODELS = [
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "google/lyria-3-pro-preview",
    "google/lyria-3-clip-preview",
    "liquid/lfm-2.5-1.2b-instruct:free",
    "liquid/lfm-2.5-1.2b-thinking:free",
    "nvidia/nemotron-nano-9b-v2:free",
    "openai/gpt-oss-120b:free",
    "openai/gpt-oss-20b:free",
    "tencent/hy3:free"
]

# 4. Creative Writing / Storytelling Models (2 unique models)
CREATIVE_MODELS = [
    "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
    "meta-llama/llama-3.3-70b-instruct:free"
]

# 5. NLP Tasks (Sentiment, Translation, NER, QA) (18 unique models)
NLP_MODELS = [
    # OpenRouter NLP/Safety (4 models)
    "meta-llama/llama-3.2-3b-instruct:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "nvidia/nemotron-3.5-content-safety:free",
    # HuggingFace NLP Inference API (14 models)
    "facebook/bart-large-mnli",
    "distilbert-base-uncased-finetuned-sst-2-english",
    "Helsinki-NLP/opus-mt-en-fr",
    "Helsinki-NLP/opus-mt-en-es",
    "Helsinki-NLP/opus-mt-en-de",
    "Helsinki-NLP/opus-mt-fr-en",
    "facebook/m2m100_418M",
    "google/pegasus-xsum",
    "facebook/bart-large-cnn",
    "sentence-transformers/all-MiniLM-L6-v2",
    "dslim/bert-base-NER",
    "dbmdz/bert-large-cased-finetuned-conll03-english",
    "deepset/roberta-base-squad2",
    "distilbert-base-cased-distilled-squad"
]

# 6. Vision / Image Generation Models (9 unique models)
VISION_MODELS = [
    "stabilityai/stable-diffusion-xl-base-1.0",
    "runwayml/stable-diffusion-v1-5",
    "prompthero/openjourney",
    "dataautogpt3/OpenDalleV1.1",
    "stabilityai/stable-diffusion-2-1",
    "CompVis/stable-diffusion-v1-4",
    "Lykon/dreamshaper-8",
    "SG161222/RealVisXL_V4.0",
    "nvidia/nemotron-nano-12b-v2-vl:free"
]

# 7. Video Generation Models (2 unique models)
VIDEO_MODELS = [
    "damo-vilab/text-to-video-ms-1.7b",
    "cerspense/zeroscope_v2_576w"
]

# Set of HuggingFace models for routing decision
HUGGINGFACE_MODELS = {
    # NLP Models
    "facebook/bart-large-mnli",
    "distilbert-base-uncased-finetuned-sst-2-english",
    "Helsinki-NLP/opus-mt-en-fr",
    "Helsinki-NLP/opus-mt-en-es",
    "Helsinki-NLP/opus-mt-en-de",
    "Helsinki-NLP/opus-mt-fr-en",
    "facebook/m2m100_418M",
    "google/pegasus-xsum",
    "facebook/bart-large-cnn",
    "sentence-transformers/all-MiniLM-L6-v2",
    "dslim/bert-base-NER",
    "dbmdz/bert-large-cased-finetuned-conll03-english",
    "deepset/roberta-base-squad2",
    "distilbert-base-cased-distilled-squad",
    # Vision Models
    "stabilityai/stable-diffusion-xl-base-1.0",
    "runwayml/stable-diffusion-v1-5",
    "prompthero/openjourney",
    "dataautogpt3/OpenDalleV1.1",
    "stabilityai/stable-diffusion-2-1",
    "CompVis/stable-diffusion-v1-4",
    "Lykon/dreamshaper-8",
    "SG161222/RealVisXL_V4.0",
    # Video Models
    "damo-vilab/text-to-video-ms-1.7b",
    "cerspense/zeroscope_v2_576w"
}

MODELS = {}

# Populate 75 Swarm agents mapping (orchestrator_1..15, coder_1..20, etc.)
for i in range(1, 16):
    MODELS[f"orchestrator_{i}"] = ORCHESTRATOR_MODELS[(i - 1) % len(ORCHESTRATOR_MODELS)]
    MODELS[f"general_{i}"] = GENERAL_MODELS[(i - 1) % len(GENERAL_MODELS)]
    MODELS[f"nlp_{i}"] = NLP_MODELS[(i - 1) % len(NLP_MODELS)]
    MODELS[f"creative_{i}"] = CREATIVE_MODELS[(i - 1) % len(CREATIVE_MODELS)]

for i in range(1, 21):
    MODELS[f"coder_{i}"] = CODER_MODELS[(i - 1) % len(CODER_MODELS)]

for i in range(1, 11):
    MODELS[f"vision_{i}"] = VISION_MODELS[(i - 1) % len(VISION_MODELS)]

MODELS["video_1"] = VIDEO_MODELS[0]
MODELS["video_2"] = VIDEO_MODELS[1]


def is_huggingface(model_id: str) -> bool:
    return model_id in HUGGINGFACE_MODELS


def get_model(category: str, index: int) -> str:
    # Normalize categories
    norm_cat = category.lower()
    if norm_cat in ["nlp_sentiment", "nlp_translation"]:
        norm_cat = "nlp"
    elif norm_cat in ["creative"]:
        norm_cat = "creative"
    elif norm_cat in ["image"]:
        norm_cat = "vision"
        
    key = f"{norm_cat}_{index}"
    fallback_key = f"{norm_cat}_1"
    
    if key in MODELS:
        return MODELS[key]
    elif fallback_key in MODELS:
        return MODELS[fallback_key]
    else:
        # Ultimate fallback
        return "meta-llama/llama-3.2-3b-instruct:free"

