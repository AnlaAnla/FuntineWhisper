import os
import json
from zipfile import ZipFile
import ffmpeg
from glob import glob
import time

def download_m3u8(url, save_folder):
    # response = requests.get(url, stream=True)
    loc_time = time.strftime('%Y-%m-%d-%H-%M-%S')
    filename = url.split('/')[-1]
    os.makedirs(save_folder, exist_ok=True)
    temp_folder = "temp"
    os.makedirs(temp_folder, exist_ok=True)
    file_path = os.path.join(save_folder, filename)

    # 使用 ffmpeg 将 M3U8 流保存为多个临时文件
    stream = ffmpeg.input(url)
    stream = ffmpeg.output(stream, os.path.join(temp_folder, 'chunk_%03d.ts'))
    ffmpeg.run(stream)

    # 合并临时文件为一个 MP4 文件
    temp_files = sorted(glob(os.path.join(temp_folder, '*.ts')))
    inputs = [ffmpeg.input(file) for file in temp_files]
    combined = ffmpeg.concat(*inputs)
    stream = ffmpeg.output(combined, file_path)
    ffmpeg.run(stream)

    # 删除临时文件
    for file in temp_files:
        os.remove(file)
    os.rmdir(temp_folder)