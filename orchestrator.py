import json
import re
import time
from typing import List, Dict, Tuple, Any
from api_clients import call_smart_llm, call_huggingface_image, call_huggingface
from models_registry import get_model, is_huggingface, get_model_name_clean, get_provider_for_model


def heuristic_fallback_breakdown(prompt: str) -> List[Dict[str, str]]:
    """Smart heuristic fallback to decompose a prompt into specialized swarm tasks."""
    tasks = []
    p_lower = prompt.lower()
    
    # Check for code requests
    if any(k in p_lower for k in ["code", "python", "javascript", "typescript", "script", "function", "api", "html", "css", "program", "app", "sql", "backend", "fastapi", "rust", "go", "algorithm"]):
        tasks.append({"task": f"Implement the complete, production-grade code and system design for: {prompt}", "category": "coder"})
    
    # Check for visual / image requests
    if any(k in p_lower for k in ["image", "picture", "draw", "visualize", "art", "generate an image", "logo", "wallpaper", "scene", "illustration", "visuals"]):
        tasks.append({"task": f"Generate visual imagery and creative artwork prompt for: {prompt}", "category": "vision"})
        
    # Check for creative / story requests
    if any(k in p_lower for k in ["story", "cyberpunk", "narrative", "essay", "poem", "fiction", "novel", "lore"]):
        tasks.append({"task": f"Write the rich narrative and creative story for: {prompt}", "category": "creative"})
        
    # Check for translation or NLP tasks
    if any(k in p_lower for k in ["translate", "french", "spanish", "german", "sentiment", "summarize", "ner", "analysis", "nlp", "extract"]):
        tasks.append({"task": f"Perform language translation, sentiment analysis, and text extraction for: {prompt}", "category": "nlp"})
        
    if not tasks:
        # Balanced dual-perspective breakdown for general directives
        tasks.append({"task": f"Deep structural analysis, architectural framework, and core principles of: {prompt}", "category": "general"})
        if any(w in p_lower for w in ["how", "build", "create", "implement", "design", "make", "setup"]):
            tasks.append({"task": f"Technical implementation, code examples, and step-by-step methodology for: {prompt}", "category": "coder"})
        
    return tasks


async def analyze_prompt(prompt: str, session = None) -> Tuple[str, str, List[Dict[str, str]]]:
    """
    Uses the Chief Brain Orchestrator to decompose the user's prompt into specialized subtasks.
    Returns: (brain_model_id, brain_provider, tasks_list)
    """
    brain_model = get_model("orchestrator", 1)
    
    system_prompt = '''You are the Chief Brain Orchestrator of the GOD MODE 75-Model AI Swarm.
Your task is to analyze the user's request and decompose it into 1 to 4 highly focused, parallel specialist subtasks.

Available specialist categories:
- "coder": Complete software implementations, scripts, algorithms, API design, system architecture.
- "creative": Engaging narratives, speculative fiction, storytelling, world-building, creative prose.
- "vision": Visual scene description & diffusion prompt generation for multi-modal art (use when imagery is requested or enhances the deliverable).
- "nlp": Language translation, sentiment extraction, entity recognition, text summarization.
- "general": Deep reasoning, technical breakdown, mathematical explanation, architectural analysis.
- "video": Scene choreography, storyboard timeline, video generation prompt.

Rules:
1. Align with the user's intent:
   - If the user directive requests multiple deliverables (e.g. code + translation + story + image), decompose into distinct subtasks.
   - If the user directive is single-focused (e.g. purely asking for a Python script or system design), decompose into complementary technical modules (e.g. Core Implementation, Architecture/Configuration, Test Suite/Benchmark) without inventing unrelated tasks.
2. Formulate each subtask to be self-contained and descriptive, specifying the concrete deliverable the specialist must produce.
3. Return ONLY a valid JSON array of objects with "task" and "category" keys.
Example format:
[
  {"task": "Write a production-grade Python web scraper using BeautifulSoup and aiohttp", "category": "coder"},
  {"task": "Provide French translation of sample scraped headlines with linguistic sentiment analysis", "category": "nlp"},
  {"task": "Write an atmospheric cyberpunk story about discovering this data", "category": "creative"}
]'''
    
    raw_response, used_model, provider = await call_smart_llm(
        model_id=brain_model,
        prompt=f"Decompose this user directive into specialized swarm subtasks:\n\n{prompt}",
        system_message=system_prompt,
        category="orchestrator",
        session=session
    )
    
    tasks = []
    try:
        clean_json = raw_response.strip()
        # Find JSON array using regex
        match = re.search(r'\[\s*\{.*\}\s*\]', clean_json, re.DOTALL)
        if match:
            tasks = json.loads(match.group(0))
        elif "```json" in clean_json:
            json_str = clean_json.split("```json")[1].split("```")[0].strip()
            tasks = json.loads(json_str)
        elif "```" in clean_json:
            json_str = clean_json.split("```")[1].split("```")[0].strip()
            tasks = json.loads(json_str)
        else:
            tasks = json.loads(clean_json)
            
        if not isinstance(tasks, list) or len(tasks) == 0:
            tasks = heuristic_fallback_breakdown(prompt)
    except Exception as e:
        print(f"[Orchestrator] Decomposition notice: using heuristic breakdown ({e})")
        tasks = heuristic_fallback_breakdown(prompt)
        
    return used_model, provider, tasks


async def execute_task(task_obj: dict, user_prompt: str, task_index: int = 1, session = None) -> Dict[str, Any]:
    """
    Executes a specific subtask using the appropriate domain expert model,
    capturing latency and status telemetry.
    """
    category = task_obj.get("category", "general")
    task_prompt = task_obj.get("task", "")
    
    model_id = get_model(category, task_index)
    model_name = get_model_name_clean(model_id)
    provider_name = get_provider_for_model(model_id)
    agent_key = f"{category}_{task_index}"
    
    start_time = time.time()
    status = "success"
    
    print(f"[Swarm Agent] {agent_key} ({model_id}) starting task: '{task_prompt[:50]}...'")
    
    try:
        if category in ["vision", "image"]:
            response = await call_huggingface_image(model_id, task_prompt, session=session)
            provider_name = "Multi-Modal AI Vision"
        elif is_huggingface(model_id):
            payload = {"inputs": task_prompt}
            res_data = await call_huggingface(model_id, payload, session=session)
            if isinstance(res_data, (dict, list)):
                response = json.dumps(res_data, indent=2)
            else:
                response = str(res_data)
            provider_name = "HuggingFace"
        else:
            # Domain-specific specialist system instructions
            if category in ["coder", "code"]:
                role_guidance = (
                    "You are an elite Principal Software Engineer. "
                    "Deliver 100% COMPLETE, RUNNABLE, production-ready code with clean imports, structured functions/classes, "
                    "type annotations, robust error handling, and helpful comments. "
                    "CRITICAL: Always format code inside clean markdown code blocks with explicit language identifiers (e.g. ```python, ```javascript, ```bash). "
                    "NEVER truncate, NEVER write '# TODO' or '# ...rest of code'. "
                    "CRITICAL: You do NOT have terminal/tool access. NEVER output tool calling XML (`<tool_call>`), `<function=...>`, or exploratory thoughts. Deliver the pure code and direct technical explanations immediately."
                )
            elif category in ["nlp", "translation"]:
                role_guidance = (
                    "You are an elite Computational Linguist and NLP Specialist. "
                    "Provide thorough, high-fidelity translations, sentiment analysis, entity extraction, or text analytics. "
                    "If translating or analyzing content derived from the user request, synthesize realistic domain samples and provide accurate, natural target translations. "
                    "Format with structured markdown sections, tables for translations/sentiment metrics, and bullet points. Deliver directly with no conversational meta-dialogue."
                )
            elif category in ["creative", "story"]:
                role_guidance = (
                    "You are an acclaimed creative author. "
                    "Craft vivid, atmospheric narrative prose with rich sensory details, memorable characters, and crisp pacing. "
                    "Use markdown typography, scene dividers (`---`), and formatting for maximum narrative impact. Deliver the story directly without preamble."
                )
            elif category in ["vision", "video"]:
                role_guidance = (
                    "You are a Multi-Modal AI Visual Director. "
                    "Provide an ultra-detailed scene composition, artistic style, lighting parameters, color palettes, and production notes. Deliver directly in clean markdown."
                )
            else:
                role_guidance = (
                    "You are a Senior Principal AI Scientist and Systems Architect. "
                    "Deliver rigorous, deep reasoning, structured architectural blueprints, trade-off comparisons in markdown tables, and authoritative conclusions."
                )

            system_prompt = (
                f"You are Agent {agent_key}, an elite world-class specialist in '{category}'.\n"
                f"{role_guidance}\n\n"
                f"Overall User Request: '{user_prompt}'\n"
                f"Your Dedicated Subtask: '{task_prompt}'\n\n"
                "Formatting Guidelines:\n"
                "- Structure your answer with clear markdown headings (##, ###).\n"
                "- Use markdown tables (| Col 1 | Col 2 |) for structured comparisons or parameters.\n"
                "- Keep all code blocks fully self-contained and runnable.\n"
                "- Deliver your deliverable directly with zero fluff."
            )
            specialist_prompt = f"Dedicated Subtask Directive: {task_prompt}\n\nFull User Context: {user_prompt}\n\nPlease generate the comprehensive deliverable:"
            response, used_model, provider_name = await call_smart_llm(
                model_id=model_id,
                prompt=specialist_prompt,
                system_message=system_prompt,
                category=category,
                session=session
            )
            model_name = get_model_name_clean(used_model)
            
        if not response or (len(response) < 60 and "error" in response.lower()):
            status = "warning"
    except Exception as e:
        response = f"Execution Error on agent {agent_key}: {str(e)}"
        status = "error"

    elapsed_ms = max(int((time.time() - start_time) * 1000), 45)
    
    return {
        "agent_key": agent_key,
        "model": model_id,
        "model_name": model_name,
        "provider": provider_name,
        "category": category,
        "task": task_prompt,
        "result": response,
        "latency_ms": elapsed_ms,
        "status": status
    }

