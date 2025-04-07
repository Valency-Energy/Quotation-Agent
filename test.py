import requests
import json

# API URL
BASE_URL = "http://127.0.0.1:8000"
QUOTATION_ENDPOINT = f"{BASE_URL}/api/quotations/"

# Sample request payload
payload = {
    "system_capacity_kw": 5,
    "installation_type": "residential",
    "location": "New Delhi",
}

# Send POST request
response = requests.post(QUOTATION_ENDPOINT, json=payload)

# Print response
if response.status_code == 200:
    print("Quotation Response:")
    print(json.dumps(response.json(), indent=4))
else:
    print(f"Error: {response.status_code}")
    print(response.text)
