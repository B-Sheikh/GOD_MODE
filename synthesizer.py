import json
from api_clients import call_smart_llm
from models_registry import get_model, get_model_name_clean, get_provider_for_model

async def synthesize_results(prompt: str, executed_tasks: list, session = None):
    """
    Compiles raw domain expert results into a cohesive, publication-quality presentation,
    ensuring code blocks, translations, analysis, and images are preserved in full.
    """
    # Choose top reasoning synthesizer model (Gemini 2.5 Flash has 1M context, or GPT-OSS 120B)
    formatter_model = get_model("orchestrator", 1)
    
    # Collect generated images and use lightweight tokens to keep LLM token usage ultra-low
    images = {}
    raw_text = ""
    for idx, item in enumerate(executed_tasks):
        result_text = str(item.get("result", "")).strip()
        agent_key = item.get("agent_key", item.get("model", f"Agent_{idx+1}"))
        task_title = item.get("task", f"Task {idx+1}")
        cat = item.get("category", "General")
        
        # Check for data:image data URI
        if "data:image" in result_text:
            img_token = f"<!-- GODMODE_IMAGE_DELIVERABLE_{len(images) + 1} -->"
            images[img_token] = f'<div class="generated-image-card"><img src="{result_text}" alt="{task_title}" class="zoomable-artifact" /></div>'
            raw_text += f"Agent [{agent_key}] ({cat.upper()}) completed visual deliverable for '{task_title}':\n{img_token}\n\n"
        else:
            raw_text += f"Agent [{agent_key}] ({cat.upper()} Specialist) completed task '{task_title}':\n{result_text}\n\n"
         
    system_prompt = (
        "You are the Chief Presentation Synthesizer in the GOD MODE 75-Model AI Swarm. "
        "Your mission is to unify and orchestrate the deliverables from all domain specialist agents "
        "into a cohesive, authoritative, publication-quality final deliverable.\n\n"
        "Structural & Typography Rules:\n"
        "1. Structure your output with clean, hierarchical markdown:\n"
        "   - # Compelling Main Title\n"
        "   - Executive Summary / Architecture Overview\n"
        "   - ## Thematic Domain Sections (Technical Implementation, Deep Analysis, Narrative, etc.)\n"
        "   - Markdown Tables (| Feature | Implementation | Notes |) for structured comparisons\n"
        "   - > **Key Architecture Insights** or Callout Notes where relevant\n"
        "2. CRITICAL: PRESERVE ALL CODE BLOCKS 100% IN FULL. Never truncate, summarize, or omit code. "
        "   Retain all syntax and language tags (```python, ```typescript, ```bash, etc.). Ensure imports and error handling are intact.\n"
        "3. Preserve all narrative stories, translations, and deep explanations in complete, rich detail.\n"
        "4. If image tokens like `<!-- GODMODE_IMAGE_DELIVERABLE_X -->` exist, PRESERVE them verbatim.\n"
        "5. Deliver the unified document directly. Do NOT include conversational meta-announcements "
        "   like 'Here is the synthesized deliverable' or 'The agents have completed their tasks'."
    )
    
    formatter_prompt = (
        f"User Original Directive:\n{prompt}\n\n"
        f"Specialist Agent Deliverables:\n{raw_text}\n\n"
        "Assemble the definitive, publication-quality final deliverable following all structural rules:"
    )
    
    formatted_summary, used_model, provider_name = await call_smart_llm(
        model_id=formatter_model,
        prompt=formatter_prompt,
        system_message=system_prompt,
        category="orchestrator",
        session=session
    )
    formatter_name = get_model_name_clean(used_model)
    
    # Fallback if synthesis call failed or returned empty
    if not formatted_summary or len(formatted_summary.strip()) < 40 or "Error" in formatted_summary[:20]:
        sections = [
            f"# GOD MODE Swarm Deliverable\n\n",
            f"> **Directive:** *{prompt}*\n\n",
            f"### Executive Summary\n"
            f"The 75-model swarm successfully orchestrated and executed {len(executed_tasks)} specialized subtasks in parallel across distributed neural nodes.\n\n"
            f"---\n\n"
        ]
        for item in executed_tasks:
            task_title = item.get("task", "Specialist Subtask")
            res = str(item.get("result", "")).strip()
            cat = item.get("category", "General")
            agent_key = item.get("agent_key", "specialist")
            model_disp = item.get("model_name", item.get("model", "Swarm Model"))
            
            sections.append(f"## {task_title}\n")
            sections.append(f"*Domain: {cat.title()} | Agent: `{agent_key}` ({model_disp})*\n\n")
            
            if "data:image" in res:
                sections.append(f'<div class="generated-image-card"><img src="{res}" alt="{task_title}" class="zoomable-artifact" /></div>\n\n')
            else:
                sections.append(f"{res}\n\n")
            sections.append("---\n\n")
            
        formatted_summary = "".join(sections)
    else:
        # Rehydrate image tokens with full image tags
        for token, img_tag in images.items():
            if token in formatted_summary:
                formatted_summary = formatted_summary.replace(token, img_tag)
            elif img_tag not in formatted_summary:
                formatted_summary = f"{formatted_summary}\n\n### Visual Deliverable\n{img_tag}\n"
    
    return {
        "synthesizer_model": used_model,
        "synthesizer_name": formatter_name,
        "provider": provider_name,
        "summary": f"Synthesized outputs from {len(executed_tasks)} swarm agents.",
        "formatted_output": formatted_summary,
        "results": executed_tasks
    }

