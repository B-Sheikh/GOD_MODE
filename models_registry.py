# models_registry.py
"""
GOD MODE AI Swarm - 75+ Model Registry
Maps specialized AI models to swarm roles, domain experts, and multi-modal generators.
Supports 100% Free Tiers across Google Gemini, Groq, OpenRouter, and Hugging Face.
"""

from typing import Dict, List, Any

# Provider Model Definitions
GROQ_MODELS = {
    "qwen/qwen3.8-27b": "Groq Qwen 3.8 27B",
    "qwen/qwen3.6-27b": "Groq Qwen 3.6 27B",
    "groq/compound": "Groq Compound MoE",
    "groq/compound-mini": "Groq Compound Mini",
    "openai/gpt-oss-20b": "Groq GPT-OSS 20B",
    "allam-2-7b": "Groq ALLaM 2 7B"
}

GEMINI_MODELS = {
    "gemini-2.5-flash": "Google Gemini 2.5 Flash",
    "gemini-flash-latest": "Google Gemini Flash Latest",
    "gemini-3.6-flash": "Google Gemini 3.6 Flash",
    "gemini-3.5-flash": "Google Gemini 3.5 Flash",
    "gemma-4-31b-it": "Google Gemma 4 31B IT",
    "gemma-4-26b-a4b-it": "Google Gemma 4 26B MoE"
}

# 1. Orchestration & Brain Models (Top reasoning & planning LLMs)
ORCHESTRATOR_MODELS = [
    "gemini-2.5-flash",
    "qwen/qwen3.8-27b",
    "google/gemma-4-31b-it:free",
    "groq/compound",
    "minimax/minimax-m3:free",
    "gemini-flash-latest",
    "z-ai/glm-5.2:free",
    "qwen/qwen3.6-27b",
    "google/gemma-4-26b-a4b-it:free",
    "openai/gpt-oss-20b",
    "minimax/minimax-m2.7:free",
    "gemini-3.6-flash",
    "groq/compound-mini",
    "cohere/north-mini-code:free",
    "gemini-2.5-flash"
]

# 2. Coder / Software Engineering Models
CODER_MODELS = [
    "qwen/qwen3.8-27b",
    "gemini-2.5-flash",
    "cohere/north-mini-code:free",
    "poolside/laguna-s-2.1:free",
    "qwen/qwen3.6-27b",
    "google/gemma-4-31b-it:free",
    "groq/compound",
    "z-ai/glm-5.2:free",
    "gemini-flash-latest",
    "google/gemma-4-26b-a4b-it:free",
    "minimax/minimax-m3:free",
    "openai/gpt-oss-20b",
    "poolside/laguna-s-2.1:free",
    "gemini-3.6-flash",
    "qwen/qwen3.8-27b",
    "groq/compound-mini",
    "cohere/north-mini-code:free",
    "google/gemma-4-31b-it:free",
    "qwen/qwen3.6-27b",
    "gemini-2.5-flash"
]

# 3. General Reasoning & Synthesis Models
GENERAL_MODELS = [
    "gemini-2.5-flash",
    "qwen/qwen3.8-27b",
    "google/gemma-4-31b-it:free",
    "groq/compound",
    "minimax/minimax-m3:free",
    "gemini-flash-latest",
    "z-ai/glm-5.2:free",
    "openai/gpt-oss-20b",
    "google/gemma-4-26b-a4b-it:free",
    "minimax/minimax-m2.7:free",
    "gemini-3.6-flash",
    "groq/compound-mini",
    "inclusionai/ling-3.0-flash-fin:free",
    "qwen/qwen3.6-27b",
    "gemini-2.5-flash"
]

# 4. Creative Writing / Storytelling Models
CREATIVE_MODELS = [
    "minimax/minimax-m3:free",
    "gemini-2.5-flash",
    "google/gemma-4-31b-it:free",
    "groq/compound",
    "minimax/minimax-m2.7:free",
    "qwen/qwen3.8-27b",
    "z-ai/glm-5.2:free",
    "gemini-flash-latest",
    "google/gemma-4-26b-a4b-it:free",
    "qwen/qwen3.6-27b"
]

# 5. NLP Specialized Models (Sentiment, Translation, NER, QA, Summarization)
NLP_MODELS = [
    "gemini-2.5-flash",
    "allam-2-7b",
    "google/gemma-4-31b-it:free",
    "qwen/qwen3.8-27b",
    "z-ai/glm-5.2:free",
    "groq/compound",
    "inclusionai/ling-3.0-flash-fin:free",
    "gemini-flash-latest",
    "minimax/minimax-m3:free",
    "openai/gpt-oss-20b"
]

# 6. Vision / Image Generation Models
VISION_MODELS = [
    "black-forest-labs/FLUX.1-schnell",
    "stabilityai/stable-diffusion-xl-base-1.0",
    "prompthero/openjourney",
    "dataautogpt3/OpenDalleV1.1",
    "stabilityai/stable-diffusion-2-1",
    "CompVis/stable-diffusion-v1-4",
    "Lykon/dreamshaper-8",
    "SG161222/RealVisXL_V4.0",
    "runwayml/stable-diffusion-v1-5",
    "black-forest-labs/FLUX.1-schnell"
]

# 7. Video Generation Models
VIDEO_MODELS = [
    "damo-vilab/text-to-video-ms-1.7b",
    "cerspense/zeroscope_v2_576w",
    "ali-vilab/text-to-video-ms-1.7b",
    "guoyww/animatediff-motion-adapter-v1-5-2",
    "ByteDance/AnimateDiff-Lightning"
]

# Set of HuggingFace models for routing decision
HUGGINGFACE_MODELS = {
    # Vision Models
    "stabilityai/stable-diffusion-xl-base-1.0",
    "runwayml/stable-diffusion-v1-5",
    "prompthero/openjourney",
    "dataautogpt3/OpenDalleV1.1",
    "stabilityai/stable-diffusion-2-1",
    "CompVis/stable-diffusion-v1-4",
    "Lykon/dreamshaper-8",
    "SG161222/RealVisXL_V4.0",
    "black-forest-labs/FLUX.1-schnell",
    # Video Models
    "damo-vilab/text-to-video-ms-1.7b",
    "cerspense/zeroscope_v2_576w",
    "ali-vilab/text-to-video-ms-1.7b",
    "guoyww/animatediff-motion-adapter-v1-5-2",
    "ByteDance/AnimateDiff-Lightning"
}

# 75-Agent Swarm Mapping (orchestrator_1..15, coder_1..20, general_1..15, creative_1..10, nlp_1..10, vision_1..10, video_1..5)
MODELS: Dict[str, str] = {}

for i in range(1, 16):
    MODELS[f"orchestrator_{i}"] = ORCHESTRATOR_MODELS[(i - 1) % len(ORCHESTRATOR_MODELS)]
    MODELS[f"general_{i}"] = GENERAL_MODELS[(i - 1) % len(GENERAL_MODELS)]

for i in range(1, 21):
    MODELS[f"coder_{i}"] = CODER_MODELS[(i - 1) % len(CODER_MODELS)]

for i in range(1, 11):
    MODELS[f"creative_{i}"] = CREATIVE_MODELS[(i - 1) % len(CREATIVE_MODELS)]
    MODELS[f"nlp_{i}"] = NLP_MODELS[(i - 1) % len(NLP_MODELS)]
    MODELS[f"vision_{i}"] = VISION_MODELS[(i - 1) % len(VISION_MODELS)]

for i in range(1, 6):
    MODELS[f"video_{i}"] = VIDEO_MODELS[(i - 1) % len(VIDEO_MODELS)]


def get_provider_for_model(model_id: str) -> str:
    """Identifies the target provider for a given model ID."""
    if model_id in GEMINI_MODELS or model_id.startswith("gemini-") or model_id.startswith("gemma-"):
        return "Google Gemini"
    elif model_id in GROQ_MODELS or model_id.startswith("groq/") or model_id.startswith("qwen/qwen3") or model_id.startswith("openai/gpt-oss") or model_id == "allam-2-7b":
        return "Groq"
    elif is_huggingface(model_id):
        return "HuggingFace"
    else:
        return "OpenRouter"


def is_huggingface(model_id: str) -> bool:
    return model_id in HUGGINGFACE_MODELS


def is_groq(model_id: str) -> bool:
    return model_id in GROQ_MODELS or model_id.startswith("groq/") or model_id.startswith("qwen/qwen3") or model_id.startswith("openai/gpt-oss") or model_id == "allam-2-7b"


def is_gemini(model_id: str) -> bool:
    return model_id in GEMINI_MODELS or model_id.startswith("gemini-") or model_id.startswith("gemma-")


def get_model(category: str, index: int = 1) -> str:
    """
    Returns the exact model ID for a given category and agent index.
    """
    norm_cat = category.lower().strip()
    if norm_cat in ["nlp_sentiment", "nlp_translation", "sentiment", "translation", "ner", "qa"]:
        norm_cat = "nlp"
    elif norm_cat in ["story", "creative_writing"]:
        norm_cat = "creative"
    elif norm_cat in ["image", "drawing", "visual", "art"]:
        norm_cat = "vision"
    elif norm_cat in ["code", "programming", "developer", "script"]:
        norm_cat = "coder"
    elif norm_cat in ["brain", "planner", "orchestration"]:
        norm_cat = "orchestrator"
    elif norm_cat not in ["orchestrator", "coder", "general", "creative", "nlp", "vision", "video"]:
        norm_cat = "general"

    key = f"{norm_cat}_{index}"
    fallback_key = f"{norm_cat}_1"

    if key in MODELS:
        return MODELS[key]
    elif fallback_key in MODELS:
        return MODELS[fallback_key]
    else:
        return "gemini-2.5-flash"


def get_model_name_clean(model_id: str) -> str:
    """Returns a clean display name from a model ID."""
    if model_id in GEMINI_MODELS:
        return GEMINI_MODELS[model_id]
    if model_id in GROQ_MODELS:
        return GROQ_MODELS[model_id]
    if "/" in model_id:
        name = model_id.split("/")[-1]
    else:
        name = model_id
    return name.replace(":free", " (Free)").replace("-", " ").replace("_", " ").title()


def get_all_models_list() -> List[Dict[str, Any]]:
    """Returns a structured list of all 75 models in the swarm for the UI."""
    items = []
    for agent_key, model_id in MODELS.items():
        category = agent_key.split("_")[0]
        provider = get_provider_for_model(model_id)
        
        items.append({
            "agent_key": agent_key,
            "model_id": model_id,
            "name": get_model_name_clean(model_id),
            "category": category,
            "provider": provider,
            "is_free": True,
            "is_huggingface": is_huggingface(model_id),
            "is_groq": is_groq(model_id),
            "is_gemini": is_gemini(model_id)
        })
    return items


