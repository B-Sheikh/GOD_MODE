import os
import time
import asyncio
import aiohttp
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from orchestrator import analyze_prompt, execute_task
from synthesizer import synthesize_results
from verifier import verify_output
from models_registry import get_all_models_list, get_model_name_clean
from api_clients import (
    get_gemini_key,
    get_groq_key,
    get_openrouter_key, 
    get_huggingface_token,
    get_active_providers,
    update_api_keys, 
    test_gemini_connection,
    test_groq_connection,
    test_openrouter_connection, 
    test_huggingface_connection
)

app = FastAPI(
    title="GOD MODE 75-Model Swarm Engine",
    description="Autonomous multi-agent orchestration architecture utilizing 75 specialized AI models.",
    version="2.0.0"
)

# Enable CORS for local web and Electron environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

class KeyUpdateRequest(BaseModel):
    gemini_key: Optional[str] = None
    groq_key: Optional[str] = None
    openrouter_key: Optional[str] = None
    huggingface_token: Optional[str] = None
    save_to_env: bool = True

class KeyTestRequest(BaseModel):
    provider: str # "gemini", "groq", "openrouter", or "huggingface"
    key: Optional[str] = None


@app.post("/godmode")
async def godmode_endpoint(request: PromptRequest):
    """
    Main entrypoint for the GOD MODE Swarm.
    Decomposes the prompt, routes concurrently to domain specialists,
    synthesizes outputs, and verifies final delivery.
    """
    start_total_time = time.time()
    prompt_str = request.prompt.strip()
    print(f"\n[GOD MODE] Initiating Swarm for: '{prompt_str[:80]}...'")
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Brain Orchestration
        brain_model, brain_provider, tasks = await analyze_prompt(prompt_str, session=session)
        brain_name = get_model_name_clean(brain_model)
        
        # Step 2: Concurrent Swarm Execution
        category_counts = {}
        execution_coroutines = []
        for t in tasks:
            cat = t.get("category", "general")
            category_counts[cat] = category_counts.get(cat, 0) + 1
            execution_coroutines.append(
                execute_task(t, prompt_str, task_index=category_counts[cat], session=session)
            )
            
        executed_tasks = await asyncio.gather(*execution_coroutines)
        
        # Step 3: Synthesis
        synth_data = await synthesize_results(prompt_str, executed_tasks, session=session)
        
        # Step 4: Verification
        final_verified_text, verifier_model_id, verifier_model_name, verifier_provider = await verify_output(
            prompt_str, 
            synth_data["formatted_output"], 
            session=session
        )
        
        total_latency_ms = max(int((time.time() - start_total_time) * 1000), 120)
        
        return {
            "status": "success",
            "prompt": prompt_str,
            "tasks_executed": len(executed_tasks),
            "total_latency_ms": total_latency_ms,
            "active_providers": get_active_providers(),
            "orchestrator": {
                "model": brain_model,
                "model_name": brain_name,
                "provider": brain_provider,
                "tasks_planned": len(tasks)
            },
            "tasks": executed_tasks,
            "synthesizer": {
                "model": synth_data.get("synthesizer_model"),
                "model_name": synth_data.get("synthesizer_name"),
                "provider": synth_data.get("provider"),
                "summary": synth_data.get("summary")
            },
            "verifier": {
                "model": verifier_model_id,
                "model_name": verifier_model_name,
                "provider": verifier_provider
            },
            "output": final_verified_text
        }


@app.get("/api/status")
async def get_system_status():
    """Returns system diagnostic status and API key configuration state."""
    gem_key = get_gemini_key()
    grq_key = get_groq_key()
    or_key = get_openrouter_key()
    hf_tok = get_huggingface_token()
    active_providers = get_active_providers()
    
    return {
        "status": "online" if active_providers else "demo_mode",
        "total_models": 75,
        "active_providers_count": len(active_providers),
        "active_providers": active_providers,
        "gemini": {
            "configured": bool(gem_key),
            "masked_key": f"{gem_key[:6]}...{gem_key[-4:]}" if len(gem_key) > 10 else ("Configured" if gem_key else "Missing")
        },
        "groq": {
            "configured": bool(grq_key),
            "masked_key": f"{grq_key[:6]}...{grq_key[-4:]}" if len(grq_key) > 10 else ("Configured" if grq_key else "Missing")
        },
        "openrouter": {
            "configured": bool(or_key),
            "masked_key": f"{or_key[:6]}...{or_key[-4:]}" if len(or_key) > 10 else ("Configured" if or_key else "Missing")
        },
        "huggingface": {
            "configured": bool(hf_tok),
            "masked_token": f"{hf_tok[:4]}...{hf_tok[-4:]}" if len(hf_tok) > 8 else ("Configured" if hf_tok else "Missing")
        }
    }


@app.get("/api/models")
async def get_models_endpoint():
    """Returns all 75 registered AI models with categories and metadata."""
    return {"models": get_all_models_list(), "total": len(get_all_models_list())}


@app.get("/api/keys")
async def get_keys_endpoint():
    """Returns key configuration status and previews."""
    gem_key = get_gemini_key()
    grq_key = get_groq_key()
    or_key = get_openrouter_key()
    hf_tok = get_huggingface_token()
    
    return {
        "gemini_configured": bool(gem_key),
        "groq_configured": bool(grq_key),
        "openrouter_configured": bool(or_key),
        "huggingface_configured": bool(hf_tok),
        "gemini_preview": f"{gem_key[:6]}...{gem_key[-4:]}" if len(gem_key) > 10 else "",
        "groq_preview": f"{grq_key[:6]}...{grq_key[-4:]}" if len(grq_key) > 10 else "",
        "openrouter_preview": f"{or_key[:6]}...{or_key[-4:]}" if len(or_key) > 10 else "",
        "huggingface_preview": f"{hf_tok[:4]}...{hf_tok[-4:]}" if len(hf_tok) > 8 else ""
    }


@app.post("/api/keys")
async def update_keys_endpoint(request: KeyUpdateRequest):
    """Updates API keys in memory and writes to .env file."""
    update_api_keys(
        gemini_key=request.gemini_key,
        groq_key=request.groq_key,
        openrouter_key=request.openrouter_key,
        huggingface_token=request.huggingface_token,
        save_to_env=request.save_to_env
    )
    return {"status": "success", "message": "API keys updated successfully!"}


@app.post("/api/keys/test")
async def test_keys_endpoint(request: KeyTestRequest):
    """Tests connectivity for a given API provider."""
    p = request.provider.lower().strip()
    if p in ["gemini", "google"]:
        success, msg = await test_gemini_connection(request.key)
        return {"provider": "gemini", "success": success, "message": msg}
    elif p == "groq":
        success, msg = await test_groq_connection(request.key)
        return {"provider": "groq", "success": success, "message": msg}
    elif p == "openrouter":
        success, msg = await test_openrouter_connection(request.key)
        return {"provider": "openrouter", "success": success, "message": msg}
    elif p in ["huggingface", "hf"]:
        success, msg = await test_huggingface_connection(request.key)
        return {"provider": "huggingface", "success": success, "message": msg}
    else:
        return {"success": False, "message": f"Unknown provider '{request.provider}'"}


# Mount static desktop/web UI files
static_dir = os.path.join(os.path.dirname(__file__), "jarvis-desktop")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(static_dir, "index.html"))

    @app.get("/styles.css")
    async def serve_css():
        return FileResponse(os.path.join(static_dir, "styles.css"))

    @app.get("/renderer.js")
    async def serve_js():
        return FileResponse(os.path.join(static_dir, "renderer.js"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)

