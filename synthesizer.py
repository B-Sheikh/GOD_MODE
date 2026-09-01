import json
from api_clients import call_smart_llm
from models_registry import get_model, get_model_name_clean, get_provider_for_model

async def synthesize_results(prompt: str, executed_tasks: list, session = None):
    """
    Compiles raw domain expert results into a cohesive, publication-quality presentation,
    ensuring code blocks, translations, analysis, and images are preserved in full.
    """
    formatter_model = get_model("orchestrator", 2)
    
    # Collect generated images and use lightweight tokens to keep LLM token usage ultra-low
    images = {}
    raw_text = ""
    for item in executed_tasks:
        result_text = str(item.get("result", ""))
        agent_key = item.get("agent_key", item.get("model", "Agent"))
        task_title = item.get("task", "Task")
        cat = item.get("category", "General")
        
        # Check for data:image data URI
        if "data:image" in result_text:
            img_token = f"<!-- GODMODE_IMAGE_DELIVERABLE_{len(images) + 1} -->"
            images[img_token] = f'<img src="{result_text}" alt="{task_title}" />'
            raw_text += f"Agent [{agent_key}] ({cat.upper()}) completed visual task '{task_title}':\n{img_token}\n\n"
        else:
            raw_text += f"Agent [{agent_key}] ({cat.upper()} - {item.get('model_name', item.get('model', ''))}) completed task '{task_title}':\n{result_text}\n\n"
         
    system_prompt = (
        "You are the Chief Presentation Synthesizer Agent in the GOD MODE AI Swarm. "
        "Your mission is to unify and present the deliverables from the specialized domain agents "
        "into a cohesive, beautifully structured, master-grade final deliverable.\n\n"
        "Crucial Rules:\n"
        "1. Present the final answer directly with elegant markdown organization and clear typography.\n"
        "2. CRITICAL: PRESERVE ALL CODE BLOCKS IN FULL. Do NOT summarize or truncate code. Keep full syntax and language tags (```python, ```javascript, etc.).\n"
        "3. Preserve all narrative stories, translations, and deep explanations in full detail.\n"
        "4. If image tokens like `<!-- GODMODE_IMAGE_DELIVERABLE_X -->` exist, PRESERVE them verbatim.\n"
        "5. Do NOT include meta-talk like 'Here is the synthesized data' or 'The agents have completed their tasks'. Deliver the pure, unified masterpiece directly."
    )
    
    formatter_prompt = f"User Request: {prompt}\n\nSpecialist Agent Deliverables:\n{raw_text}\n\nPlease assemble the unified final deliverable."
    
    formatted_summary, used_model, provider_name = await call_smart_llm(
        model_id=formatter_model,
        prompt=formatter_prompt,
        system_message=system_prompt,
        category="orchestrator",
        session=session
    )
    formatter_name = get_model_name_clean(used_model)
    
    # Fallback if synthesis call failed or returned empty
    if not formatted_summary or len(formatted_summary.strip()) < 30 or "Error" in formatted_summary[:20]:
        sections = [f"## ⚡ GOD MODE Swarm Deliverable\n\n"]
        for item in executed_tasks:
            task_title = item.get("task", "Task")
            res = item.get("result", "")
            cat = item.get("category", "General")
            if "data:image" in str(res):
                sections.append(f"### 🎨 Visual Deliverable\n<img src=\"{res}\" alt=\"{task_title}\" />\n\n")
            elif "```" in str(res):
                sections.append(f"### 💻 Technical Implementation\n{res}\n\n")
            else:
                sections.append(f"### 🌐 {cat.title()} Specialist Output\n{res}\n\n")
        formatted_summary = "".join(sections)
    else:
        # Rehydrate image tokens with full image tags
        for token, img_tag in images.items():
            if token in formatted_summary:
                formatted_summary = formatted_summary.replace(token, img_tag)
            elif img_tag not in formatted_summary:
                formatted_summary = f"{formatted_summary}\n\n### 🎨 Visual Deliverable\n{img_tag}\n"
    
    return {
        "synthesizer_model": used_model,
        "synthesizer_name": formatter_name,
        "provider": provider_name,
        "summary": f"Synthesized outputs from {len(executed_tasks)} swarm agents.",
        "formatted_output": formatted_summary,
        "results": executed_tasks
    }

