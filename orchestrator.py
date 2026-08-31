import json
from api_clients import call_openrouter
from models_registry import get_model

async def analyze_prompt(prompt: str, session = None):
    """
    Uses the Brain model to break down the user prompt into subtasks.
    """
    brain_model = get_model("orchestrator", 2)
    
    system_prompt = '''
You are the Orchestrator of a massive AI Swarm system. 
Break down the user's request into a list of tasks and assign each task to a specialized model category.
Available categories:
- coder
- creative
- vision
- general
- nlp_sentiment
- nlp_translation

Respond ONLY with a JSON list of dictionaries. Example:
[
  {"task": "Write a python script", "category": "coder"},
  {"task": "Write a story", "category": "creative"}
]
'''
    
    response = await call_openrouter(
        model=brain_model, 
        prompt=prompt, 
        system_message=system_prompt,
        session=session
    )
    
    try:
        # Extract JSON from potential markdown blocks
        clean_json = response.strip()
        if "```json" in clean_json:
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        tasks = json.loads(clean_json)
        return brain_model, tasks
    except Exception as e:
        print(f"Error parsing orchestrator response: {e}\nRaw: {response}")
        return brain_model, [{"task": prompt, "category": "general"}]

async def execute_task(task_obj: dict, user_prompt: str, task_index: int = 1, session = None):
    """
    Executes a specific subtask using the appropriate model, 
    providing the original user context.
    """
    category = task_obj.get("category", "general")
    task_prompt = task_obj.get("task", "")
    
    # Pick a model from the registry using the dynamic task_index
    from api_clients import call_openrouter, call_huggingface_image, call_huggingface
    from models_registry import get_model, is_huggingface
    
    model_id = get_model(category, task_index)
    
    print(f"Executing: '{task_prompt}' on {model_id} (Index: {task_index})")
    
    if category in ["vision", "image"]:
        print(f"Routing to Image Generation API for task: {task_prompt}")
        response = await call_huggingface_image(model_id, task_prompt, session=session)
    elif is_huggingface(model_id):
        print(f"Routing to HuggingFace NLP API for task: {task_prompt}")
        payload = {"inputs": task_prompt}
        res_data = await call_huggingface(model_id, payload, session=session)
        if isinstance(res_data, (dict, list)):
            import json
            response = json.dumps(res_data, indent=2)
        else:
            response = str(res_data)
    else:
        system_prompt = (
            f"You are a specialized expert in the category: {category}. "
            f"The user has requested the following overall goal: '{user_prompt}'. "
            f"Your specific task to help achieve this goal is: '{task_prompt}'."
        )
        response = await call_openrouter(model_id, task_prompt, system_prompt, session=session)
    
    return {
        "model": model_id,
        "task": task_prompt,
        "result": response
    }
