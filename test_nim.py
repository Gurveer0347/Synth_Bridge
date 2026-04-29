import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("NVIDIA_NIM_API_KEY", "")

response = requests.get(
    "https://integrate.api.nvidia.com/v1/models",
    headers={"Authorization": f"Bearer {api_key}"}
)
if response.status_code == 200:
    models = response.json().get("data", [])
    print(f"Total models: {len(models)}")
    for m in models:
        if "mini" in m["id"].lower():
            print("Found:", m["id"])
else:
    print("Error:", response.status_code, response.text)
