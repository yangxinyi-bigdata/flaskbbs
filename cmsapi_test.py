# pip install requests
# Authorization:"Bearer {{jwt}}"

import requests

headers = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcxNjg4MjQxMywianRpIjoiZGZiZDcyMDMtMDA0Yi00NjQwLWIzMGItNGJiOTUzMmNlNWIzIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImhzbzVhRzdGZGI4NGNtN3F2eXFUTjMiLCJuYmYiOjE3MTY4ODI0MTMsImNzcmYiOiJjYzlmOGEwMC1kMTgwLTQyN2QtOGRhYy1kMTZkNzVmNjFlYmIiLCJleHAiOjE3MTc3NDY0MTN9.SSorzBxC9vdLiTZJZRPHCVwxjG7oAEEshbHbrrT3B1o"
}
response = requests.get("http://127.0.0.1:5000/cmsapi", headers=headers)
print(response.text)
