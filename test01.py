import requests

# curl -X GET http://192.168.66.117:8081/api/projects/{id}/export?exportType=JSON&download_all_tasks=true

label_studio_url = "http://192.168.66.117:8081"
label_studio_token = "6e5785f3e71fcd05a3ae10d25931b9db8991aeb3"
project_id = 10

url = f"{label_studio_url}/api/projects/{project_id}/export?exportType=JSON"
headers = {
    "Authorization": "Token 6e5785f3e71fcd05a3ae10d25931b9db8991aeb3",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
print(response)
print(response.json())