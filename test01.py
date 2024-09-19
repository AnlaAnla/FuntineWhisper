import requests
import json

# 第一个curl命令
url = "http://localhost:8080/api/projects"
headers = {
    "Authorization": "Token 6e5785f3e71fcd05a3ae10d25931b9db8991aeb3",
    "Content-Type": "application/json"
}
data = {
    "title": "音频与转录项目",
    "label_config": "<View><Audio name=\"audio\" value=\"$audio\" /><TextArea name=\"transcription\" value=\"$transcription\" toName=\"audio\" editable=\"true\" rows=\"5\" /></View>"
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.status_code)
print(response.text)

# 第二个curl命令
url = "http://localhost:8080/api/projects/3/import"
headers = {
    "Authorization": "Token 6c85a9d2d73398271149196e1eddb63e32f9276e",
    "Content-Type": "application/json"
}
data = [
    {
        "audio": "http://truenas.lan:9000/tencent-ts-records/audio0.mp3",
        "transcription": "对随便划随便划"
    },
    {
        "audio": "http://truenas.lan:9000/tencent-ts-records/audio1.mp3",
        "transcription": "没事你有的时候划开"
    },
    {
        "audio": "http://truenas.lan:9000/tencent-ts-records/audio2.mp3",
        "transcription": "划破那箱子也无所谓"
    }
]

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.status_code)
print(response.text)