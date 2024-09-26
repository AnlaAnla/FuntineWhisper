import os
import json
import pandas as pd
import numpy as np
import requests


def get_label(_project_id):
    url = f"{label_studio_url}/api/projects/{_project_id}/export?exportType=JSON"
    headers = {
        "Authorization": f"Token {label_studio_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json()


# 把导出的数据进行处理
if __name__ == '__main__':
    label_studio_url = "http://192.168.66.117:8081"
    label_studio_token = "6e5785f3e71fcd05a3ae10d25931b9db8991aeb3"

    audio_data_dir_path = r"C:\Code\ML\Audio\card_audio_data02"
    project_id = 10

    json_datas = get_label(project_id)

    metadata = []
    for json_data in json_datas:
        audio_path = 'audio/' + os.path.split(json_data['data']['audio'])[-1]
        metadata.append([audio_path, json_data['data']['transcription']])

    meta_data = np.array(metadata)
    meta_data = pd.DataFrame(meta_data, columns=['file_name', 'sentence'])
    print(meta_data)
    meta_data.to_csv(os.path.join(audio_data_dir_path, "metadata.csv"), encoding='utf-8', index=False)

    print('处理结束')
