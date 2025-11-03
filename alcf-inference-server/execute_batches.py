import json

import requests
from alcf_inference_token import get_access_token

# Get your access token
access_token = get_access_token()

# Define headers and URL
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}
url = "https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1/batches"

# Submit batch request
data = {
    "model": "openai/gpt-oss-120b",
    "input_file": "/eagle/EVITA/nsynovic/jsonl/output_0001.jsonl",
    "output_folder_path": "/eagle/EVITA/nsynovic/jsonl/output",
}

response = requests.post(url, headers=headers, json=data)
print(response.json())

url = "https://inference-api.alcf.anl.gov/resource_server/v1/batches"

# List all batches
response = requests.get(url, headers=headers)
print(response.json())
