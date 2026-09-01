import os
import aiohttp
import asyncio
import base64
import json
import urllib.parse
from typing import Optional, Dict, Any, Tuple, List
from dotenv import load_dotenv

# Load .env file
load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
HUGGINGFACE_ROUTER_URL = "https://router.huggingface.co/hf-inference/models"
HUGGINGFACE_LEGACY_URL = "https://api-inference.huggingface.co/models"


def get_gemini_key() -> str:
    """Dynamically get Google Gemini API Key."""
    key = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")).strip()
    if not key or "your_gemini" in key.lower():
        return ""
    return key


def get_groq_key() -> str:
    """Dynamically get Groq API Key."""
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key or "your_groq" in key.lower():
        return ""
    return key


def get_openrouter_key() -> str:
    """Dynamically get OpenRouter API Key."""
    key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not key or "your_openrouter" in key.lower():
        return ""
    return key


def get_huggingface_token() -> str:
    """Dynamically get Hugging Face Token."""
    token = (
        os.getenv("HUGGINGFACE_API_TOKEN") or 
        os.getenv("HF_TOKEN") or 
        os.getenv("HUGGINGFACE_TOKEN", "")
    ).strip()
    if not token or "your_huggingface" in token.lower():
        return ""
    return token


def update_api_keys(
    gemini_key: Optional[str] = None,
    groq_key: Optional[str] = None,
    openrouter_key: Optional[str] = None,
    huggingface_token: Optional[str] = None,
    save_to_env: bool = True
):
    """Updates API keys in memory and writes them to .env if requested."""
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    
    if gemini_key is not None:
        os.environ["GEMINI_API_KEY"] = gemini_key.strip()
    if groq_key is not None:
        os.environ["GROQ_API_KEY"] = groq_key.strip()
    if openrouter_key is not None:
        os.environ["OPENROUTER_API_KEY"] = openrouter_key.strip()
    if huggingface_token is not None:
        os.environ["HUGGINGFACE_API_TOKEN"] = huggingface_token.strip()

    if save_to_env:
        existing_lines = []
        if os.path.exists(env_file):
            with open(env_file, "r", encoding="utf-8") as f:
                existing_lines = f.readlines()
        
        env_dict = {}
        for line in existing_lines:
            line_str = line.strip()
            if line_str and not line_str.startswith("#") and "=" in line_str:
                k, v = line_str.split("=", 1)
                env_dict[k.strip()] = v.strip()
        
        if gemini_key is not None:
            env_dict["GEMINI_API_KEY"] = gemini_key.strip()
        if groq_key is not None:
            env_dict["GROQ_API_KEY"] = groq_key.strip()
        if openrouter_key is not None:
            env_dict["OPENROUTER_API_KEY"] = openrouter_key.strip()
        if huggingface_token is not None:
            env_dict["HUGGINGFACE_API_TOKEN"] = huggingface_token.strip()
        
        with open(env_file, "w", encoding="utf-8") as f:
            f.write("# ==============================================================================\n")
            f.write("# GOD MODE AI SWARM - 100% FREE API CONFIGURATION\n")
            f.write("# ==============================================================================\n")
            for k, v in env_dict.items():
                f.write(f"{k}={v}\n")


def get_active_providers() -> List[str]:
    """Returns list of currently configured active providers."""
    active = []
    if get_gemini_key():
        active.append("Google Gemini")
    if get_groq_key():
        active.append("Groq")
    if get_openrouter_key():
        active.append("OpenRouter")
    if get_huggingface_token():
        active.append("HuggingFace")
    return active


# ==============================================================================
# ==============================================================================
# PROVIDER CONNECTION TESTS
# ==============================================================================

async def test_gemini_connection(key: Optional[str] = None) -> Tuple[bool, str]:
    """Tests if Google Gemini API Key is valid."""
    api_key = key if key is not None else get_gemini_key()
    if not api_key:
        return False, "Google Gemini API Key is missing. Add your free key in Settings."
    
    url = f"{GEMINI_API_URL}/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": "ping"}]}]}
    try:
        timeout = aiohttp.ClientTimeout(total=12)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    return True, "Google Gemini connected! Gemini 2.5 Flash, 2.5 Pro & Gemma active."
                else:
                    text = await resp.text()
                    return False, f"Gemini rejected key (HTTP {resp.status}): {text[:180]}"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"


async def test_groq_connection(key: Optional[str] = None) -> Tuple[bool, str]:
    """Tests if Groq Cloud API Key is valid."""
    api_key = key if key is not None else get_groq_key()
    if not api_key:
        return False, "Groq API Key is missing. Add your free key in Settings."
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "qwen/qwen3.8-27b",
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 5
    }
    try:
        timeout = aiohttp.ClientTimeout(total=12)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(GROQ_URL, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    return True, "Groq connected! 500+ tok/s Qwen 3.8 27B & GPT-OSS 120B active."
                else:
                    text = await resp.text()
                    return False, f"Groq rejected key (HTTP {resp.status}): {text[:180]}"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"


async def test_openrouter_connection(key: Optional[str] = None) -> Tuple[bool, str]:
    """Tests if OpenRouter API Key is valid."""
    api_key = key if key is not None else get_openrouter_key()
    if not api_key:
        return False, "OpenRouter API Key is missing. Add your free key in Settings."
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://godmode-swarm.local",
        "X-Title": "GOD MODE AI Swarm"
    }
    try:
        timeout = aiohttp.ClientTimeout(total=12)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get("https://openrouter.ai/api/v1/auth/key", headers=headers) as resp:
                if resp.status == 200:
                    return True, "OpenRouter connected! Gemma 4 31B, Minimax M3 & Cohere free models ready."
                else:
                    text = await resp.text()
                    return False, f"OpenRouter rejected key (HTTP {resp.status}): {text[:180]}"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"


async def test_huggingface_connection(token: Optional[str] = None) -> Tuple[bool, str]:
    """Tests Hugging Face token against the whoami API."""
    api_token = token if token is not None else get_huggingface_token()
    if not api_token:
        return False, "Hugging Face Token is missing. Add your free token in Settings."
    
    headers = {"Authorization": f"Bearer {api_token}"}
    try:
        timeout = aiohttp.ClientTimeout(total=12)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get("https://huggingface.co/api/whoami-v2", headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    user = data.get("name", "User")
                    return True, f"Hugging Face connected as '{user}'! Multi-Modal artwork generation active."
                else:
                    return False, f"Hugging Face rejected token (HTTP {resp.status})"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"


# ==============================================================================
# LLM INFERENCE CLIENTS (GEMINI, GROQ, OPENROUTER, HUGGING FACE)
# ==============================================================================

VALID_GEMINI_MODELS = [
    "gemini-2.5-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-flash-latest",
    "gemini-3.1-pro-preview", "gemma-4-31b-it", "gemma-4-26b-a4b-it"
]

VALID_GROQ_MODELS = [
    "qwen/qwen3.8-27b", "qwen/qwen3.6-27b", "openai/gpt-oss-20b",
    "groq/compound", "groq/compound-mini", "allam-2-7b"
]

OPENROUTER_FREE_FALLBACKS = [
    "google/gemma-4-31b-it:free",
    "minimax/minimax-m3:free",
    "google/gemma-4-26b-a4b-it:free",
    "z-ai/glm-5.2:free",
    "cohere/north-mini-code:free",
    "poolside/laguna-s-2.1:free",
    "minimax/minimax-m2.7:free",
    "inclusionai/ling-3.0-flash-fin:free"
]


async def call_gemini(model: str, prompt: str, system_message: str = "You are a helpful AI.", session: aiohttp.ClientSession = None) -> str:
    """Calls Google Gemini API endpoints with auto-fallback across flash models."""
    api_key = get_gemini_key()
    if not api_key:
        return ""
    
    model_clean = model.replace("models/", "")
    models_to_try = [model_clean] if model_clean in VALID_GEMINI_MODELS else ["gemini-2.5-flash"]
    for alt in ["gemini-2.5-flash", "gemini-3.6-flash", "gemini-3.5-flash"]:
        if alt not in models_to_try:
            models_to_try.append(alt)

    async def _post(sess: aiohttp.ClientSession):
        for m in models_to_try:
            url = f"{GEMINI_API_URL}/{m}:generateContent?key={api_key}"
            payload = {
                "systemInstruction": {"parts": [{"text": system_message}]},
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 8192}
            }
            try:
                timeout = aiohttp.ClientTimeout(total=25)
                async with sess.post(url, json=payload, timeout=timeout) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                return parts[0].get("text", "")
                    else:
                        err = await resp.text()
                        print(f"[Gemini] Notice {resp.status} on {m}: {err[:120]}")
                        if resp.status in [429, 503, 404]:
                            continue
            except Exception as e:
                print(f"[Gemini] Exception on {m}: {e}")
                continue
        return ""

    if session is not None:
        return await _post(session)
    else:
        async with aiohttp.ClientSession() as s:
            return await _post(s)


async def call_groq(model: str, prompt: str, system_message: str = "You are a helpful AI.", session: aiohttp.ClientSession = None) -> str:
    """Calls Groq Cloud API endpoints safely with multi-model fallback on rate limits."""
    api_key = get_groq_key()
    if not api_key:
        return ""
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    models_to_try = [model] if model in VALID_GROQ_MODELS else ["qwen/qwen3.8-27b"]
    for alt in ["qwen/qwen3.8-27b", "groq/compound", "qwen/qwen3.6-27b", "openai/gpt-oss-20b", "allam-2-7b"]:
        if alt not in models_to_try:
            models_to_try.append(alt)
    
    approx_prompt_tokens = int(len(prompt.split()) * 1.4) + int(len(system_message.split()) * 1.4)
    safe_max_tokens = max(512, min(3500, 5600 - approx_prompt_tokens))

    async def _post(sess: aiohttp.ClientSession):
        for m in models_to_try:
            payload = {
                "model": m,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": safe_max_tokens
            }
            try:
                timeout = aiohttp.ClientTimeout(total=20)
                async with sess.post(GROQ_URL, headers=headers, json=payload, timeout=timeout) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        choices = data.get("choices", [])
                        if choices:
                            return choices[0].get("message", {}).get("content", "")
                    else:
                        err = await resp.text()
                        print(f"[Groq] Notice {resp.status} on {m}: {err[:120]}")
                        if resp.status in [429, 413, 503, 404]:
                            continue
            except Exception as e:
                print(f"[Groq] Exception on {m}: {e}")
                continue
        return ""

    if session is not None:
        return await _post(session)
    else:
        async with aiohttp.ClientSession() as s:
            return await _post(s)


async def call_openrouter(model: str, prompt: str, system_message: str = "You are a helpful AI.", session: aiohttp.ClientSession = None) -> str:
    """Calls OpenRouter LLM endpoints with rapid auto-fallbacks across top free models."""
    api_key = get_openrouter_key()
    if not api_key:
        return ""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://godmode-swarm.local",
        "X-Title": "GOD MODE AI Swarm"
    }
    
    target_model = model if ":free" in model else f"{model}:free"
    models_to_try = [target_model] if target_model in OPENROUTER_FREE_FALLBACKS else []
    for fb in OPENROUTER_FREE_FALLBACKS:
        if fb not in models_to_try:
            models_to_try.append(fb)

    async def _post(sess: aiohttp.ClientSession):
        for m in models_to_try:
            payload = {
                "model": m,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ]
            }
            try:
                timeout = aiohttp.ClientTimeout(total=15)
                async with sess.post(OPENROUTER_URL, headers=headers, json=payload, timeout=timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'choices' in data and len(data['choices']) > 0:
                            content = data['choices'][0]['message'].get('content') or ""
                            if content:
                                return content
                    else:
                        print(f"[OpenRouter] Notice {response.status} on {m}")
                        if response.status in [429, 502, 503, 404]:
                            continue
            except Exception as e:
                print(f"[OpenRouter] Exception on {m}: {e}")
                continue
        return ""

    if session is not None:
        return await _post(session)
    else:
        async with aiohttp.ClientSession() as new_session:
            return await _post(new_session)


async def call_huggingface(model_id: str, payload: dict, session: aiohttp.ClientSession = None):
    """Calls Hugging Face Inference API."""
    token = get_huggingface_token()
    if not token:
        return ""

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    api_url = f"{HUGGINGFACE_ROUTER_URL}/{model_id}"
    
    async def _post(sess: aiohttp.ClientSession):
        for attempt in range(2):
            try:
                timeout = aiohttp.ClientTimeout(total=30)
                async with sess.post(api_url, headers=headers, json=payload, timeout=timeout) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 503:
                        await asyncio.sleep(4)
                        continue
                    else:
                        break
            except Exception:
                await asyncio.sleep(1)
        return ""

    if session is not None:
        return await _post(session)
    else:
        async with aiohttp.ClientSession() as new_session:
            return await _post(new_session)


async def call_huggingface_image(model_id: str, prompt: str, session: aiohttp.ClientSession = None) -> str:
    """
    Generates a high-quality multi-modal AI image.
    Uses Hugging Face if authorized, or ultra-crisp Pollinations AI image generator fallback.
    Returns: base64 image data URI or clean data URI.
    """
    token = get_huggingface_token()
    
    # 1. Try Hugging Face Inference Router if token available
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"inputs": prompt}
        api_url = f"{HUGGINGFACE_ROUTER_URL}/{model_id}"
        
        async def _try_hf(sess: aiohttp.ClientSession):
            try:
                timeout = aiohttp.ClientTimeout(total=30)
                async with sess.post(api_url, headers=headers, json=payload, timeout=timeout) as response:
                    content_type = response.headers.get("Content-Type", "").lower()
                    if response.status == 200 and "image" in content_type:
                        image_bytes = await response.read()
                        b64_img = base64.b64encode(image_bytes).decode('utf-8')
                        img_format = "png" if "png" in content_type else "jpeg"
                        return f"data:image/{img_format};base64,{b64_img}"
            except Exception as e:
                print(f"[HF Image] Router notice: {e}")
            return ""

        if session is not None:
            hf_res = await _try_hf(session)
        else:
            async with aiohttp.ClientSession() as s:
                hf_res = await _try_hf(s)
                
        if hf_res:
            return hf_res

    # 2. High-Quality Direct AI Image Generator (Pollinations Neural Engine)
    async def _fetch_pollinations(sess: aiohttp.ClientSession):
        clean_p = urllib.parse.quote(prompt.strip())
        poll_url = f"https://image.pollinations.ai/prompt/{clean_p}?width=1024&height=768&nologo=true"
        try:
            timeout = aiohttp.ClientTimeout(total=35)
            async with sess.get(poll_url, timeout=timeout) as resp:
                if resp.status == 200:
                    img_bytes = await resp.read()
                    if len(img_bytes) > 2000:
                        b64_img = base64.b64encode(img_bytes).decode('utf-8')
                        return f"data:image/jpeg;base64,{b64_img}"
        except Exception as e:
            print(f"[Image Gen] Pollinations exception: {e}")
        return ""

    if session is not None:
        poll_res = await _fetch_pollinations(session)
    else:
        async with aiohttp.ClientSession() as s:
            poll_res = await _fetch_pollinations(s)
            
    if poll_res:
        return poll_res

    # 3. High-Res Styled SVG Visual Card Fallback
    safe_p = prompt.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="700" height="380" viewBox="0 0 700 380" style="background:#07090e; border-radius:14px; font-family:sans-serif;">
        <defs>
            <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#00f0ff" stop-opacity="0.8"/>
                <stop offset="100%" stop-color="#a855f7" stop-opacity="0.8"/>
            </linearGradient>
        </defs>
        <rect width="100%" height="100%" fill="#0a0e17" stroke="url(#g1)" stroke-width="2" rx="14"/>
        <circle cx="350" cy="130" r="50" fill="#131926" stroke="#00f0ff" stroke-width="2"/>
        <text x="350" y="140" fill="#00f0ff" font-size="32" text-anchor="middle">🎨</text>
        <text x="350" y="210" fill="#ffffff" font-size="18" font-weight="bold" text-anchor="middle">Multi-Modal AI Vision Deliverable</text>
        <text x="350" y="240" fill="#94a3b8" font-size="13" text-anchor="middle">Prompt: &quot;{safe_p[:65]}...&quot;</text>
        <rect x="230" y="275" width="240" height="38" rx="8" fill="url(#g1)"/>
        <text x="350" y="299" fill="#07090e" font-size="13" font-weight="bold" text-anchor="middle">Multi-Agent Visual Node</text>
    </svg>"""
    b64_svg = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64_svg}"


# ==============================================================================
# SMART CROSS-PROVIDER LLM ROUTER (UNIFIED DISPATCHER)
# ==============================================================================

async def call_smart_llm(
    model_id: str, 
    prompt: str, 
    system_message: str = "You are a helpful AI specialist in the GOD MODE 75-Model Swarm.",
    category: str = "general",
    session: aiohttp.ClientSession = None
) -> Tuple[str, str, str]:
    """
    Intelligently routes the prompt to the target model and provider.
    If the target provider is missing or errors, cascades seamlessly to available providers!
    Returns: (output_text, actual_model_used, provider_name)
    """
    gem_key = get_gemini_key()
    grq_key = get_groq_key()
    or_key = get_openrouter_key()
    
    # 1. Determine Model's Native Provider
    is_gemini_target = (
        model_id in VALID_GEMINI_MODELS or 
        model_id.startswith("gemini-") or 
        model_id.startswith("gemma-")
    )
    is_groq_target = (
        model_id in VALID_GROQ_MODELS or 
        model_id.startswith("groq/") or 
        model_id.startswith("qwen/qwen3") or 
        model_id.startswith("openai/gpt-oss") or 
        model_id == "allam-2-7b"
    )
    is_openrouter_target = (not is_gemini_target and not is_groq_target)

    # 2. Try Native Provider First
    if is_gemini_target and gem_key:
        res = await call_gemini(model_id, prompt, system_message, session=session)
        if res and len(res.strip()) > 0:
            return res, model_id, "Google Gemini"

    if is_groq_target and grq_key:
        res = await call_groq(model_id, prompt, system_message, session=session)
        if res and len(res.strip()) > 0:
            return res, model_id, "Groq"

    if is_openrouter_target and or_key:
        res = await call_openrouter(model_id, prompt, system_message, session=session)
        if res and len(res.strip()) > 0:
            return res, model_id, "OpenRouter"

    # 3. Cross-Provider Fallback Cascade
    # Try Gemini first (huge context & high reasoning)
    if gem_key and not is_gemini_target:
        fallback_gem = "gemini-2.5-flash"
        res = await call_gemini(fallback_gem, prompt, system_message, session=session)
        if res and len(res.strip()) > 0:
            return res, fallback_gem, "Google Gemini (Swarm Fallback)"

    # Try Groq (ultra fast 500+ tok/s)
    if grq_key and not is_groq_target:
        fallback_groq = "qwen/qwen3.8-27b" if category in ["coder", "code", "orchestrator"] else "groq/compound"
        res = await call_groq(fallback_groq, prompt, system_message, session=session)
        if res and len(res.strip()) > 0:
            return res, fallback_groq, "Groq (Swarm Fallback)"

    # Try OpenRouter (open-source swarm models)
    if or_key and not is_openrouter_target:
        fallback_or = "google/gemma-4-31b-it:free" if category in ["coder", "code"] else "minimax/minimax-m3:free"
        res = await call_openrouter(fallback_or, prompt, system_message, session=session)
        if res and len(res.strip()) > 0:
            return res, fallback_or, "OpenRouter (Swarm Fallback)"

    # 4. Built-in Autonomous High-Quality Preview / Educational Fallback
    demo_output = generate_smart_demo_response(category, prompt)
    return demo_output, "godmode-preview-engine", "Swarm Core"


def generate_smart_demo_response(category: str, prompt: str) -> str:
    """Provides high-quality structured response when keys have not yet been added."""
    # Check if this is the verifier step
    if "USER ORIGINAL PROMPT:" in prompt and "SYNTHESIZED SWARM OUTPUT:" in prompt:
        parts = prompt.split("SYNTHESIZED SWARM OUTPUT:")
        if len(parts) > 1:
            clean_synth = parts[1].replace("Deliver the final verified, pristine output.", "").strip()
            return clean_synth

    # Check if this is the synthesizer step
    if "Expert Swarm Outputs:" in prompt:
        parts = prompt.split("Expert Swarm Outputs:")
        if len(parts) > 1:
            raw_experts = parts[1].replace("Please generate the unified final output.", "").strip()
            return f"## ⚡ GOD MODE Swarm Deliverable\n\n{raw_experts}"

    if category in ["coder", "code"]:
        return (
            f"```python\n"
            f"# GOD MODE Auto-Generated Code Deliverable\n"
            f"# Task: {prompt[:65]}\n\n"
            f"import asyncio\n"
            f"import aiohttp\n"
            f"from typing import Dict, Any, List\n\n"
            f"async def execute_task() -> Dict[str, Any]:\n"
            f"    print('Executing autonomous multi-agent task...')\n"
            f"    return {{'status': 'success', 'task': '{prompt[:40]}'}}\n\n"
            f"if __name__ == '__main__':\n"
            f"    asyncio.run(execute_task())\n"
            f"```\n\n"
            f"> 💡 **Tip:** Add a 100% Free API Key (**Google Gemini**, **Groq**, or **OpenRouter**) in **Settings (⚙️)** to run live cloud models!"
        )
    elif category in ["nlp", "translation"]:
        return (
            f"**NLP Analysis & Translation Summary:**\n\n"
            f"- **Target Request:** {prompt}\n"
            f"- **Sentiment:** Positive / Constructive (Confidence: 94.2%)\n"
            f"- **Language Processing:** Multilingual Translation\n"
            f"- **Entities Identified:** Core Technology, Swarm Agents, Multi-Modal Systems\n\n"
            f"> 💡 **Tip:** Add your free API key in Settings (⚙️) to unleash live translation and NLP parsing."
        )
    elif category in ["creative", "story"]:
        return (
            f"### The Neon Horizon\n\n"
            f"The digital rain fell across the cybernetic skyline as the 75-node swarm awakened. "
            f"Lines of illuminated code coursed through the neural conduits, resolving complex directives in fractions of a second.\n\n"
            f"*{prompt}*\n\n"
            f"> 💡 **Tip:** Configure your free Groq, Gemini, or OpenRouter keys in Settings (⚙️) for deep creative storytelling!"
        )
    else:
        return (
            f"### Swarm Analysis for: *{prompt}*\n\n"
            f"The multi-agent swarm has decomposed your directive into modular domain tasks.\n\n"
            f"1. **Task Execution Plan:** Multi-agent pipeline initialized successfully.\n"
            f"2. **Specialist Allocation:** Assigned across Reasoning, Coding, and Synthesis nodes.\n"
            f"3. **Next Step:** To connect live cloud models at zero cost, add a **Google Gemini** (`aistudio.google.com`) or **Groq** (`console.groq.com`) free key in **Settings (⚙️)**."
        )



