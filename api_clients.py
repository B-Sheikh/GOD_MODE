import os
import aiohttp
import base64
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

async def call_openrouter(model: str, prompt: str, system_message: str = "You are a helpful AI.", session: aiohttp.ClientSession = None) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
    }
    
    async def _post(sess):
        try:
            async with sess.post(OPENROUTER_URL, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'choices' in data and len(data['choices']) > 0:
                        return data['choices'][0]['message']['content']
                    return f"Error: Unexpected response format: {data}"
                else:
                    text_response = await response.text()
                    # Try a sequence of fallback free models in case of rate limits or service issues
                    fallbacks = [
                        "meta-llama/llama-3.3-70b-instruct:free",
                        "google/gemma-4-31b-it:free",
                        "meta-llama/llama-3.2-3b-instruct:free",
                        "liquid/lfm-2.5-1.2b-instruct:free",
                        "openai/gpt-oss-20b:free"
                    ]
                    print(f"Model {model} failed with status {response.status}. Trying fallbacks...")
                    for fb_model in fallbacks:
                        if fb_model == model:
                            continue
                        print(f"Attempting fallback model: {fb_model}")
                        payload["model"] = fb_model
                        try:
                            async with sess.post(OPENROUTER_URL, headers=headers, json=payload) as fallback_res:
                                if fallback_res.status == 200:
                                    fallback_data = await fallback_res.json()
                                    if 'choices' in fallback_data and len(fallback_data['choices']) > 0:
                                        return fallback_data['choices'][0]['message']['content']
                                else:
                                    print(f"Fallback {fb_model} failed with status {fallback_res.status}")
                        except Exception as fb_err:
                            print(f"Fallback {fb_model} exception: {fb_err}")
                    return f"Error {response.status}: {text_response}"
        except Exception as e:
            return f"OpenRouter Call Failed: {str(e)}"

    if session is not None:
        return await _post(session)
    else:
        async with aiohttp.ClientSession() as new_session:
            return await _post(new_session)

async def call_huggingface(model_id: str, payload: dict, session: aiohttp.ClientSession = None):
    import asyncio
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
    
    async def _post(sess):
        for attempt in range(5):
            try:
                async with sess.post(API_URL, headers=headers, json=payload) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 503:
                        try:
                            res_json = await response.json()
                            est_time = min(float(res_json.get("estimated_time", 10.0)), 15.0)
                        except Exception:
                            est_time = 10.0
                        print(f"HuggingFace Model {model_id} is loading. Retrying in {est_time} seconds (Attempt {attempt+1}/5)...")
                        await asyncio.sleep(est_time)
                    else:
                        text = await response.text()
                        if "currently loading" in text:
                            try:
                                res_json = await response.json()
                                est_time = min(float(res_json.get("estimated_time", 10.0)), 15.0)
                            except Exception:
                                est_time = 10.0
                            print(f"HuggingFace Model {model_id} is loading (json response). Retrying in {est_time} seconds (Attempt {attempt+1}/5)...")
                            await asyncio.sleep(est_time)
                            continue
                        return f"Error {response.status}: {text}"
            except Exception as e:
                if attempt == 4:
                    return f"HuggingFace Call Failed: {str(e)}"
                await asyncio.sleep(2)
        return "Error: HuggingFace model failed to load after 5 attempts."

    if session is not None:
        return await _post(session)
    else:
        async with aiohttp.ClientSession() as new_session:
            return await _post(new_session)

async def call_huggingface_image(model_id: str, prompt: str, session: aiohttp.ClientSession = None):
    import asyncio
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"
    }
    API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
    payload = {"inputs": prompt}
    
    async def _post(sess):
        for attempt in range(5):
            try:
                async with sess.post(API_URL, headers=headers, json=payload) as response:
                    if response.status == 200:
                        content_type = response.headers.get("Content-Type", "")
                        if "json" in content_type:
                            res_json = await response.json()
                            if "currently loading" in res_json.get("error", ""):
                                est_time = min(float(res_json.get("estimated_time", 10.0)), 15.0)
                                print(f"HuggingFace Image Model {model_id} is loading. Retrying in {est_time} seconds (Attempt {attempt+1}/5)...")
                                await asyncio.sleep(est_time)
                                continue
                        image_bytes = await response.read()
                        b64_img = base64.b64encode(image_bytes).decode('utf-8')
                        return f"data:image/jpeg;base64,{b64_img}"
                    elif response.status == 503:
                        try:
                            res_json = await response.json()
                            est_time = min(float(res_json.get("estimated_time", 10.0)), 15.0)
                        except Exception:
                            est_time = 10.0
                        print(f"HuggingFace Image Model {model_id} is loading. Retrying in {est_time} seconds (Attempt {attempt+1}/5)...")
                        await asyncio.sleep(est_time)
                    else:
                        text = await response.text()
                        if "currently loading" in text:
                            try:
                                res_json = await response.json()
                                est_time = min(float(res_json.get("estimated_time", 10.0)), 15.0)
                            except Exception:
                                est_time = 10.0
                            print(f"HuggingFace Image Model {model_id} is loading (fallback text check). Retrying in {est_time} seconds (Attempt {attempt+1}/5)...")
                            await asyncio.sleep(est_time)
                            continue
                        return f"Error {response.status}: {text}"
            except Exception as e:
                if attempt == 4:
                    return f"Image Generation Failed (Network/API Error): {str(e)}"
                await asyncio.sleep(2)
        return "Error: HuggingFace Image model failed to load after 5 attempts."

    if session is not None:
        return await _post(session)
    else:
        async with aiohttp.ClientSession() as new_session:
            return await _post(new_session)
