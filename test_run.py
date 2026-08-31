import requests

# This is a sample script to test the GOD MODE swarm locally.

url = "http://127.0.0.1:8000/godmode"
payload = {
    "prompt": "Write a python script to scrape a website, translate it to French, write a short cyberpunk story about a hacker finding the data, and summarize the story's sentiment."
}

try:
    print(f"Sending prompt to GOD MODE Swarm:\n'{payload['prompt']}'\n")
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        print("\n" + "="*50)
        print(f"STATUS: {data['status']}")
        print(f"TASKS EXECUTED: {data['tasks_executed']}")
        print("="*50 + "\n")
        print(data['output'])
    else:
        print(f"Failed with status code: {response.status_code}")
        print(response.text)
except requests.exceptions.ConnectionError:
    print("Error: Could not connect to the GOD MODE API.")
    print("Make sure you have started the server using: .\\venv\\Scripts\\python main.py")
