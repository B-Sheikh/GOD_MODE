import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

print("==================================================")
print("   GOD MODE 75-MODEL SWARM - VERIFICATION SUITE   ")
print("==================================================")

# 1. Test System Status
try:
    print("\n[1/3] Checking Swarm System Status (/api/status)...")
    res = requests.get(f"{BASE_URL}/api/status", timeout=5)
    if res.status_code == 200:
        status_data = res.json()
        print(f" -> System Status:    {status_data.get('status').upper()}")
        print(f" -> Total Models:     {status_data.get('total_models')}")
        print(f" -> Active Providers: {status_data.get('active_providers_count', 0)} {status_data.get('active_providers', [])}")
        print(f" -> Google Gemini:    {status_data.get('gemini', {}).get('masked_key')}")
        print(f" -> Groq Cloud:       {status_data.get('groq', {}).get('masked_key')}")
        print(f" -> OpenRouter:       {status_data.get('openrouter', {}).get('masked_key')}")
        print(f" -> Hugging Face:     {status_data.get('huggingface', {}).get('masked_token')}")
    else:
        print(f" -> Failed: HTTP {res.status_code}")
except Exception as e:
    print(f" -> Connection failed: {e}")

# 2. Test Model Registry
try:
    print("\n[2/3] Checking Swarm Models Registry (/api/models)...")
    res = requests.get(f"{BASE_URL}/api/models", timeout=5)
    if res.status_code == 200:
        models_data = res.json()
        print(f" -> Registered Agents in Swarm: {models_data.get('total')}")
        sample = models_data.get("models", [])[:4]
        for m in sample:
            print(f"    - [{m['agent_key']}] {m['name']} ({m['provider']})")
    else:
        print(f" -> Failed: HTTP {res.status_code}")
except Exception as e:
    print(f" -> Connection failed: {e}")

# 3. Test Swarm Prompt Execution
payload = {
    "prompt": "Write a python script to scrape a website, translate it to French, write a short cyberpunk story about a hacker finding the data, and summarize the story's sentiment."
}

try:
    print(f"\n[3/3] Sending Multi-Agent Prompt to Swarm Engine:\n'{payload['prompt']}'\n")
    start = time.time()
    response = requests.post(f"{BASE_URL}/godmode", json=payload, timeout=120)
    elapsed = time.time() - start
    
    if response.status_code == 200:
        data = response.json()
        print("="*50)
        print(f"STATUS:          {data['status'].upper()}")
        print(f"TASKS EXECUTED:  {data['tasks_executed']}")
        print(f"TOTAL TIME:      {elapsed:.2f}s (Engine Latency: {data.get('total_latency_ms', 0)}ms)")
        print(f"ORCHESTRATOR:    {data.get('orchestrator', {}).get('model_name')} ({data.get('orchestrator', {}).get('provider')})")
        print(f"SYNTHESIZER:     {data.get('synthesizer', {}).get('model_name')} ({data.get('synthesizer', {}).get('provider')})")
        print(f"VERIFIER:        {data.get('verifier', {}).get('model_name')} ({data.get('verifier', {}).get('provider')})")
        print("="*50 + "\n")
        print("FINAL VERIFIED OUTPUT:\n")
        print(data['output'])
    else:
        print(f"Failed with status code: {response.status_code}")
        print(response.text)
except requests.exceptions.ConnectionError:
    print("\n⚠️ Error: Could not connect to the GOD MODE API.")
    print("Start the server using: ./venv/bin/python main.py (Linux) or python main.py (Windows)")

