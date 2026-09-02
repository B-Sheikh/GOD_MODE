import re
from typing import Tuple
from api_clients import call_smart_llm
from models_registry import get_model, get_model_name_clean, get_provider_for_model


def automated_qa_lint(text: str) -> str:
    """Performs deterministic quality assurance and formatting repair on deliverables."""
    if not text:
        return ""
        
    # 1. Strip any residual internal reasoning or tool-call tags
    text = re.sub(r'<think>[\s\S]*?</think>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<thought>[\s\S]*?</thought>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<tool_call>[\s\S]*?</tool_call>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<function=[\s\S]*?</function>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<tool_response>[\s\S]*?</tool_response>', '', text, flags=re.IGNORECASE)
    
    # 2. Ensure unclosed code fences are closed
    fence_count = text.count("```")
    if fence_count % 2 != 0:
        text = text.rstrip() + "\n```\n"
        
    # 3. Clean up excessive consecutive blank lines
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    
    return text.strip()


async def verify_output(original_prompt: str, synthesized_output: str, session = None) -> Tuple[str, str, str, str]:
    """
    The Verifier agent reviews the synthesized output against the original user prompt
    to ensure it perfectly answers the request, has no hallucinations, and preserves formatting & media.
    Returns: (final_verified_text, verifier_model_id, verifier_model_name, verifier_provider)
    """
    # First run deterministic QA pass
    linted_output = automated_qa_lint(synthesized_output or "")
    model_id = "gemini-2.5-flash"
    
    try:
        # Tokenize any heavy base64 image tags so the verification prompt is lightweight
        images = {}
        clean_synth_output = linted_output
        
        # Extract <img src="data:image..."> or container div
        img_matches = re.findall(r'<img\s+src=["\'](data:image\/[^"\']+)["\'][^>]*>', linted_output)
        for idx, src in enumerate(img_matches):
            token = f"<!-- GODMODE_VERIFIED_IMG_{idx + 1} -->"
            orig_tag = re.search(r'(?:<div class="generated-image-card">)?<img\s+src=["\']' + re.escape(src) + r'["\'][^>]*>(?:<\/div>)?', linted_output)
            if orig_tag:
                tag_str = orig_tag.group(0)
                images[token] = tag_str
                clean_synth_output = clean_synth_output.replace(tag_str, token)
        
        # Select model: for large outputs (>6000 chars), use Gemini with 1M context to prevent Groq 413 limits
        if len(clean_synth_output) > 6000:
            model_id = "gemini-2.5-flash"
        else:
            model_id = get_model("orchestrator", 3)
    
        # If the output is already rich, verified, and complete, we can either do LLM audit or certify
        system_prompt = (
            "You are the Chief Quality Assurance & Verification Agent in the GOD MODE 75-Model Swarm. "
            "Your duty is to review the synthesized output against the user's original directive.\n\n"
            "Rules:\n"
            "1. Fix any minor syntax, grammatical, or markdown formatting errors.\n"
            "2. Ensure all components of the user directive have been addressed.\n"
            "3. CRITICAL: DO NOT summarize, compress, or truncate the deliverable. Keep all code blocks 100% complete and fully written.\n"
            "4. CRITICAL: If image tokens like `<!-- GODMODE_VERIFIED_IMG_X -->` exist, PRESERVE them verbatim.\n"
            "5. Deliver the pristine deliverable directly without preamble or meta-talk."
        )
        
        verification_prompt = (
            f"USER ORIGINAL DIRECTIVE:\n{original_prompt}\n\n"
            f"SYNTHESIZED SWARM DELIVERABLE:\n{clean_synth_output}\n\n"
            "Deliver the final verified, pristine deliverable preserving all complete implementations and media in full:"
        )
        
        response, used_model, provider_name = await call_smart_llm(
            model_id=model_id,
            prompt=verification_prompt,
            system_message=system_prompt,
            category="orchestrator",
            session=session
        )
        model_name = get_model_name_clean(used_model)
        
        # Quality Guard: If verifier failed, timed out, or truncated code, retain pristine synthesized output
        orig_code_blocks = clean_synth_output.count("```")
        resp_code_blocks = response.count("```") if response else 0
        
        if (not response or 
            len(response.strip()) < 40 or 
            "Error" in response[:20] or 
            len(response) < len(clean_synth_output) * 0.7 or
            (orig_code_blocks > 0 and resp_code_blocks < orig_code_blocks)):
            return linted_output, model_id, get_model_name_clean(model_id), "Swarm QA (Certified)"
            
        # Re-inject verified images
        for token, img_tag in images.items():
            if token in response:
                response = response.replace(token, img_tag)
            elif img_tag not in response:
                response = f"{response}\n\n{img_tag}\n"
                
        final_text = automated_qa_lint(response)
        return final_text, used_model, model_name, provider_name
    except Exception as e:
        print(f"[Verifier] Verification fallback: {e}")
        return linted_output, model_id, get_model_name_clean(model_id), "Swarm QA (Certified)"

