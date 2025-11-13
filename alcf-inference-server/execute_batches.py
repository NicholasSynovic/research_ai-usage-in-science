import json
from pprint import pprint as print
from time import sleep

import requests
from alcf_inference_token import get_access_token

# Get your access token
access_token = get_access_token()

# Define headers and URL
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}

# Submit batch request
url = "https://inference-api.alcf.anl.gov/resource_server/sophia/vllm/v1/batches"

data = {
    "model": "openai/gpt-oss-120b",
    "input_file": "/home/nsynovic/jsonl/output_0001.jsonl",
    "output_folder_path": "/home/nsynovic/jsonl/output",
}

response = requests.post(url, headers=headers, json=data)
print(response.json())

# url = "https://inference-api.alcf.anl.gov/resource_server/v1/batches"

# # List all batches
# while True:
#     response = requests.get(url, headers=headers)
#     print(response.json()[-1])
#     sleep(10)
