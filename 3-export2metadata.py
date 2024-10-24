import os
import json
import pandas as pd
import numpy as np
import requests


def get_label(_project_id):
    url = f"{label_studio_url}/api/projects/{_project_id}/export?exportType=JSON_MIN"
    headers = {
        "Authorization": f"Token {label_studio_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json()


def download_file(url, save_path):
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        # 打开一个文件用于写入
        with open(save_path, 'wb') as f:
            # 迭代读取数据
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # 过滤掉keep-alive的情况
                    f.write(chunk)
        print(f'文件下载成功, {save_path}: {url}')
    else:
        print('文件下载失败，错误代码:', response.status_code)


# 把导出的数据进行处理
if __name__ == '__main__':
    label_studio_url = "http://192.168.66.117:8081"
    label_studio_token = "6e5785f3e71fcd05a3ae10d25931b9db8991aeb3"

    audio_data_dir_path = r"C:\Code\ML\Audio\card_audio_data02"
    if not os.path.exists(os.path.join(audio_data_dir_path, 'audio')):
        os.mkdir(os.path.join(audio_data_dir_path, 'audio'))

    project_id = 29
    json_datas = get_label(project_id)

    metadata = []
    for json_data in json_datas:
        audio_path = 'audio/' + os.path.split(json_data['audio'])[-1]

        try:
            download_file(json_data['audio'], os.path.join(audio_data_dir_path, audio_path))
            metadata.append([audio_path, json_data['transcription']])
        except Exception as e:
            print("下载异常", e)

    meta_data = np.array(metadata)
    meta_data = pd.DataFrame(meta_data, columns=['file_name', 'sentence'])
    print(meta_data)
    meta_data.to_csv(os.path.join(audio_data_dir_path, "metadata.csv"), encoding='utf-8', index=False)

    print('处理结束')
