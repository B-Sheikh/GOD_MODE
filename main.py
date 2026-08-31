from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
import aiohttp

from orchestrator import analyze_prompt, execute_task
from synthesizer import synthesize_results
from verifier import verify_output

app = FastAPI(title="GOD MODE Swarm API")

class PromptRequest(BaseModel):
    prompt: str

@app.post("/godmode")
async def godmode_endpoint(request: PromptRequest):
    print(f"Received GOD MODE request: {request.prompt}")
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Orchestrator breaks down the prompt
        print("Brain is analyzing the prompt...")
        orchestrator_model, tasks = await analyze_prompt(request.prompt, session=session)
        
        print(f"Identified {len(tasks)} sub-tasks:")
        for t in tasks:
            print(f" - {t}")
            
        # Step 2: Route tasks to different domain expert models concurrently
        # Track index counts by category to distribute requests across the 75 models
        category_counts = {}
        execution_coroutines = []
        for t in tasks:
            cat = t.get("category", "general")
            # Increment task index for that category (1-indexed)
            category_counts[cat] = category_counts.get(cat, 0) + 1
            execution_coroutines.append(
                execute_task(t, request.prompt, task_index=category_counts[cat], session=session)
            )
            
        print("Deploying Swarm Agents...")
        # Run all model calls in parallel
        executed_tasks = await asyncio.gather(*execution_coroutines)
        
        # Step 3: Synthesize and compile results
        print("Synthesizing results...")
        final_output_dict = await synthesize_results(request.prompt, executed_tasks, session=session)
        
        # Step 4: Verification
        print("Verifying final output...")
        # Pass the formatted summary to the verifier
        final_verified_text = await verify_output(request.prompt, final_output_dict["formatted_output"], session=session)
        
        # We return ONLY the final verified text for the new simple UI
        return {"status": "success", "tasks_executed": len(tasks), "output": final_verified_text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
