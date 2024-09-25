import os
import json
import pandas as pd
import numpy as np

# 把导出的数据进行处理
if __name__ == '__main__':
    json_mini_path = r"C:\Code\ML\Audio\card_audio_data01\project-10-at-2024-09-23-09-07-87b7a955.json"
    data_save_dir = r"C:\Code\ML\Audio\card_audio_data01\project-10-at-2024-09-23-09-07-87b7a955"

    with open(json_mini_path, "r", encoding='utf-8') as f:
        json_datas = json.load(f)

    metadata = []
    for json_data in json_datas:
        audio_path = 'audio/' + os.path.split(json_data['audio'])[-1]
        metadata.append([audio_path, json_data['transcription']])

    meta_data = np.array(metadata)
    meta_data = pd.DataFrame(meta_data, columns=['file_name', 'sentence'])
    print(meta_data)
    meta_data.to_csv(os.path.join(data_save_dir, "metadata.csv"), encoding='utf-8', index=False)

    print('处理结束')
