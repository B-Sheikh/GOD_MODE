import json
import re
import time
from typing import List, Dict, Tuple, Any
from api_clients import call_smart_llm, call_huggingface_image, call_huggingface
from models_registry import get_model, is_huggingface, get_model_name_clean, get_provider_for_model


def heuristic_fallback_breakdown(prompt: str) -> List[Dict[str, str]]:
    """Heuristic fallback to decompose a prompt into specialized swarm tasks."""
    tasks = []
    p_lower = prompt.lower()
    
    # Check for code requests
    if any(k in p_lower for k in ["code", "python", "javascript", "script", "function", "api", "html", "css", "program", "app", "sql", "backend", "fastapi"]):
        tasks.append({"task": f"Implement the complete, production-grade code for: {prompt}", "category": "coder"})
    
    # Check for visual / image requests
    if any(k in p_lower for k in ["image", "picture", "draw", "visualize", "art", "generate an image", "logo", "wallpaper", "scene", "illustration"]):
        tasks.append({"task": f"Generate visual imagery and creative artwork for: {prompt}", "category": "vision"})
        
    # Check for creative / story requests
    if any(k in p_lower for k in ["story", "cyberpunk", "narrative", "essay", "poem", "fiction", "novel", "lore"]):
        tasks.append({"task": f"Write the rich narrative and creative story for: {prompt}", "category": "creative"})
        
    # Check for translation or NLP tasks
    if any(k in p_lower for k in ["translate", "french", "spanish", "german", "sentiment", "summarize", "ner", "analysis", "nlp"]):
        tasks.append({"task": f"Perform language translation, sentiment analysis, and text extraction for: {prompt}", "category": "nlp"})
        
    if not tasks:
        tasks.append({"task": prompt, "category": "general"})
        
    return tasks


async def analyze_prompt(prompt: str, session = None) -> Tuple[str, str, List[Dict[str, str]]]:
    """
    Uses the Chief Brain Orchestrator to decompose the user's prompt into specialized subtasks.
    Returns: (brain_model_id, brain_provider, tasks_list)
    """
    brain_model = get_model("orchestrator", 1)
    
    system_prompt = '''You are the Chief Brain Orchestrator of the GOD MODE 75-Model AI Swarm.
Your task is to analyze the user's request, decompose it into 1 to 4 highly focused subtasks, and assign each to a specialist category.

Available specialist categories:
- "coder": Programming, algorithms, scripts, system architecture, debugging, API design.
- "creative": Creative writing, storytelling, world-building, marketing copy, prose.
- "vision": Visual descriptions, multi-modal art, and image generation prompts.
- "nlp": Language translation, sentiment analysis, entity extraction, data summarization.
- "general": Deep reasoning, mathematical explanation, factual answers, analysis.
- "video": Video prompt generation and scene direction.

Return ONLY a valid JSON array of objects with "task" and "category" keys.
Example format:
[
  {"task": "Write a Python web scraper using BeautifulSoup", "category": "coder"},
  {"task": "Translate the scraped summary into French", "category": "nlp"},
  {"task": "Write a cyberpunk hacker story about the data", "category": "creative"}
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
            system_prompt = (
                f"You are Agent {agent_key}, an elite world-class specialist in '{category}'.\n"
                f"Overall User Request: '{user_prompt}'\n"
                f"Your Dedicated Subtask: '{task_prompt}'\n\n"
                "Instructions:\n"
                "1. Provide a comprehensive, in-depth, production-ready deliverable.\n"
                "2. If writing code, provide COMPLETE, RUNNABLE code with clean imports, structure, comments, and error handling. NEVER truncate or write placeholders (no '# TODO' or '# ...rest of code').\n"
                "3. If writing narratives, translation, or analysis, deliver rich, high-quality, articulate prose.\n"
                "4. Deliver your work directly with high authority and clarity."
            )
            specialist_prompt = f"Primary Subtask Directive: {task_prompt}\n\nFull User Context: {user_prompt}"
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

