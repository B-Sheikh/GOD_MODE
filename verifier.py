import re
from typing import Tuple
from api_clients import call_smart_llm
from models_registry import get_model, get_model_name_clean, get_provider_for_model

async def verify_output(original_prompt: str, synthesized_output: str, session = None) -> Tuple[str, str, str, str]:
    """
    The Verifier agent reviews the synthesized output against the original user prompt
    to ensure it perfectly answers the request, has no hallucinations, and preserves formatting & media.
    Returns: (final_verified_text, verifier_model_id, verifier_model_name, verifier_provider)
    """
    model_id = get_model("orchestrator", 3)
    
    # Tokenize any heavy base64 image tags so the verification prompt is lightweight
    images = {}
    clean_synth_output = synthesized_output
    
    # Extract <img src="data:image...">
    img_matches = re.findall(r'<img\s+src=["\'](data:image\/[^"\']+)["\'][^>]*>', synthesized_output)
    for idx, src in enumerate(img_matches):
        token = f"<!-- GODMODE_VERIFIED_IMG_{idx + 1} -->"
        orig_tag = re.search(r'<img\s+src=["\']' + re.escape(src) + r'["\'][^>]*>', synthesized_output)
        if orig_tag:
            tag_str = orig_tag.group(0)
            images[token] = tag_str
            clean_synth_output = clean_synth_output.replace(tag_str, token)
    
    system_prompt = (
        "You are the Chief Quality Assurance & Verification Agent in the GOD MODE 75-Model Swarm. "
        "Your duty is to review the synthesized output against the user's original request.\n\n"
        "Rules:\n"
        "1. Fix any minor syntax or formatting errors in code blocks.\n"
        "2. Ensure all parts of the user request have been fully addressed.\n"
        "3. CRITICAL: DO NOT summarize, compress, or truncate the synthesized output. Keep all code blocks 100% complete and fully written.\n"
        "4. CRITICAL: If image tokens like `<!-- GODMODE_VERIFIED_IMG_X -->` exist, PRESERVE them verbatim.\n"
        "5. Deliver the final, polished response directly without preamble or meta-talk."
    )
    
    verification_prompt = (
        f"USER ORIGINAL PROMPT:\n{original_prompt}\n\n"
        f"SYNTHESIZED SWARM OUTPUT:\n{clean_synth_output}\n\n"
        "Deliver the final verified, pristine deliverable preserving all complete implementations and media in full:"
    )
    
    try:
        response, used_model, provider_name = await call_smart_llm(
            model_id=model_id,
            prompt=verification_prompt,
            system_message=system_prompt,
            category="orchestrator",
            session=session
        )
        model_name = get_model_name_clean(used_model)
        
        # If verifier failed or drastically shortened the response, retain pristine synthesized output
        if (not response or 
            len(response.strip()) < 30 or 
            "Error" in response[:20] or 
            len(response) < len(clean_synth_output) * 0.5):
            return synthesized_output, model_id, get_model_name_clean(model_id), "Swarm QA"
            
        # Re-inject verified images
        for token, img_tag in images.items():
            if token in response:
                response = response.replace(token, img_tag)
            elif img_tag not in response:
                response = f"{response}\n\n{img_tag}\n"
                
        return response, used_model, model_name, provider_name
    except Exception as e:
        print(f"[Verifier] Verification fallback: {e}")
        return synthesized_output, model_id, get_model_name_clean(model_id), "Swarm QA"

