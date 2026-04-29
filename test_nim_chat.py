import os
import requests
from dotenv import load_dotenv
import time

load_dotenv()
api_key = os.environ.get("NVIDIA_NIM_API_KEY", "")

start = time.time()
try:
    response = requests.post(
        "https://integrate.api.nvidia.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": "meta/llama-3.1-70b-instruct",
            "messages": [{"role": "user", "content": "Respond with the word 'HELLO' and nothing else."}],
            "max_tokens": 10
        },
        timeout=30
    )
    print("Status:", response.status_code)
    print("Time:", time.time() - start)
    if response.status_code == 200:
        print("Response:", response.json()["choices"][0]["message"]["content"])
    else:
        print("Error:", response.text)
except Exception as e:
    print("Exception:", e)
