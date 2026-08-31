from api_clients import call_openrouter
from models_registry import get_model

async def verify_output(original_prompt: str, synthesized_output: str, session = None) -> str:
    """
    The Verifier agent reviews the synthesized output against the original user prompt
    to ensure it perfectly answers the request, has no hallucinations, and is formatted perfectly.
    """
    model_id = get_model("orchestrator", 1)  # Use a top-tier model for verification (e.g. Llama 3 70B)
    
    system_prompt = (
        "You are the Final Verifier Agent in a 75-model Swarm Architecture. "
        "Your job is to review the synthesized output provided by the Swarm Synthesizer, "
        "compare it to the original User Prompt, and output the absolute best, final, verified answer. "
        "If the synthesized output contains code, ensure it looks correct. "
        "If the synthesized output contains image tags (like <img src='...'>), YOU MUST PRESERVE THEM EXACTLY in your final output. "
        "Do not include any preamble about your verification process. Just output the final, polished response directly."
    )
    
    verification_prompt = (
        f"USER'S ORIGINAL PROMPT: {original_prompt}\n\n"
        f"SYNTHESIZED SWARM OUTPUT TO VERIFY:\n{synthesized_output}\n\n"
        "Please provide the final, verified, and polished output."
    )
    
    print(f"Executing Verification Agent on {model_id}...")
    response = await call_openrouter(model_id, verification_prompt, system_prompt, session=session)
    return response
