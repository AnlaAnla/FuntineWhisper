import pyaudio
import numpy as np
import requests
import queue
import threading

CHUNK = 512
audio_threshold = 50  # 语音识别阈值

flag_queue = queue.Queue()  # 清空frame的flag
data_queue = queue.Queue()  # 数据

SERVER_URL = "http://192.168.77.193:2345/recognize_audio/"  # 替换为服务器的IP地址


def record_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=CHUNK)

    frame = []
    while True:
        data = stream.read(CHUNK)
        audio_data = np.frombuffer(data, dtype=np.int16)
        if np.max(audio_data) > audio_threshold:
            print("检测到音频, 开始录音")

            low_audio_num = 0
            while True:
                for i in range(5):
                    data = stream.read(CHUNK)
                    frame.append(data)

                audio_data = b''.join(frame)
                frame = []
                audio_data = np.frombuffer(audio_data, dtype=np.int16)

                if np.max(audio_data) < audio_threshold:
                    low_audio_num += 1
                else:
                    data_queue.put(audio_data)
                    low_audio_num = 0

                if low_audio_num == 3:
                    flag_queue.put(True)


def send_audio_to_server():
    audio_data = np.array([])
    while True:
        if not data_queue.empty():
            while not data_queue.empty():
                temp_audio_data = data_queue.get().astype(np.float32) / 32768.0
                audio_data = np.concatenate((audio_data, temp_audio_data)).astype(np.float32)

            # print("发送音频到服务器...")

            # 将音频数据发送到服务器
            response = requests.post(SERVER_URL, files={'file': audio_data.tobytes()})
            if response.status_code == 200:
                print(f"\r识别结果: {response.json()['text']}", end="")
            else:
                print("识别失败")

        if not flag_queue.empty():
            audio_data = np.array([])  # 清空音频数据
            flag = flag_queue.get()
            print("\n", '_' * 10)


if __name__ == '__main__':
    t1 = threading.Thread(target=record_audio)
    t2 = threading.Thread(target=send_audio_to_server)

    t_list = [t1, t2]

    for t in t_list:
        t.start()

    print("客户端启动完毕")
    for t in t_list:
        t.join()
