import pandas as pd
from minio import Minio
import datetime
import numpy as np
import requests
import json
import os


def creat_project(project_name: str):
    url = f"{label_studio_url}/api/projects"
    headers = {
        "Authorization": f"Token {label_studio_token}",
        "Content-Type": "application/json"
    }
    data = {
        "title": project_name,
        "label_config": "<View><Audio name=\"audio\" value=\"$audio\" /><TextArea name=\"transcription\" value=\"$transcription\" toName=\"audio\" editable=\"true\" rows=\"5\" /></View>"
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(response.status_code)
    print(response.text)
    return response.json()['id']


# 上传音频数据到数据服务器
def upload_dataServer(access_key, secret_key,
                      bucket_name='label-studio-data'):
    print('连接minio')
    minio_client = Minio(remote_data_server_ip,
                         access_key=access_key,
                         secret_key=secret_key,
                         secure=False)
    print('minio成功连接')

    # 桶的名称是默认的, 取决于服务器的设置
    bucket_name = bucket_name
    # 文件夹名称
    data_dir_name = os.path.split(audio_data_dir_path)[-1]

    # 遍历本地文件夹,上传所有文件到Minio
    print(f"开始向minio上传: {audio_data_dir_path}")
    for root, dirs, files in os.walk(audio_data_dir_path):
        for file in files:
            # 构造源文件路径
            file_path = os.path.join(root, file)
            # 保留文件夹结构,构造在Minio存储桶中的对象名称
            object_name = os.path.relpath(file_path, audio_data_dir_path)
            object_name = object_name.replace('\\', '/')

            if data_dir_name:
                object_name = data_dir_name + '/' + object_name
            try:
                # 上传文件
                minio_client.fput_object(bucket_name, object_name, file_path)
                print(f'上传minio: {file_path} as {object_name}')
            except Exception as e:
                print('minio错误: ', e)
    print('minio上传结束')


# 上传数据到label-studio, 音频数据从数据服务器映射
def upload_labelStudio(project_id):
    remote_data_server_url = f"http://{remote_data_server_ip}/label-studio-data/"
    url = f"{label_studio_url}/api/projects/{project_id}/import"
    headers = {
        "Authorization": "Token 6e5785f3e71fcd05a3ae10d25931b9db8991aeb3",
        "Content-Type": "application/json"
    }

    metadata = pd.read_csv(os.path.join(audio_data_dir_path, "pre_metadata.csv"))
    metadata = np.array(metadata)

    data_dir_name = os.path.split(audio_data_dir_path)[-1]
    data = []
    for i in range(len(metadata)):
        data.append({
            "audio": f"{remote_data_server_url}/{data_dir_name}/audio/{metadata[i][0]}",
            "transcription": metadata[i][1]
        })

    print("开始上传label-studio")
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(response.status_code)
    print(response.text)

    print("数据导入结束")


if __name__ == '__main__':
    label_studio_token = "6e5785f3e71fcd05a3ae10d25931b9db8991aeb3"
    audio_data_dir_path = r"C:\Code\ML\Audio\card_audio_data02"
    remote_data_server_ip = "truenas.lan:9000"
    label_studio_url = "http://192.168.66.117:8081"

    if "audio" not in os.listdir(audio_data_dir_path):
        print(f"文件结构异常, 请检查目录: {audio_data_dir_path}")

    upload_dataServer(access_key='TQUDCSxXiw5D5hPBbm5J',
                      secret_key='DB63Vk3qU81LQ0szSM7DyrL9rfswJG2qmjJ0BAqU')

    # 如果有项目就改成自己的id
    # project_id = 10
    project_id = creat_project("test02")
    upload_labelStudio(project_id)
