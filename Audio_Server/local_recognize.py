import pyaudio
import numpy as np
import wave
import time
from faster_whisper import WhisperModel
import torch
import os
import queue
from zhconv import convert
import threading


DEBUG = False

os.environ["KMP_DUPLICATE_LIB_OK"] = 'True'
CHUNK = 512
audio_threshold = 50  # 语音识别阈值

flag_queue = queue.Queue()  # 清空frame的flag
data_queue = queue.Queue()  # 数据


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
            print("检测到音频, 开始实时识别")

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

                if DEBUG:
                    print("1 -- 添加数据, 此时low num: ", low_audio_num )


def recognize_audio():
    audio_data = np.array([])
    while True:
        if not data_queue.empty():
            while not data_queue.empty():
                temp_audio_data = data_queue.get().astype(np.float32) / 32768.0
                audio_data = np.concatenate((audio_data, temp_audio_data)).astype(np.float32)

            if DEBUG:
                print('----------------------------')
                print('这里识别: ', audio_data.shape)
                print('----------------------------')

            segments, info = model.transcribe(audio_data, beam_size=5, language="zh", vad_filter=True,
                                              vad_parameters=dict(min_silence_duration_ms=500))
            if segments:
                paragraph = ''
                for segment in segments:
                    text = convert(segment.text, 'zh-cn')
                    paragraph += text
                print(f"\r识别文字: {paragraph}", end="")

        if not flag_queue.empty():
            audio_data = np.array([])
            flag = flag_queue.get()
            print("\n", '_'*10)

            if DEBUG:
                print('清空 frame', flag)


if __name__ == '__main__':
    print("Loading model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using {device} device.")
    model = WhisperModel("base", device=device, local_files_only=True)

    t1 = threading.Thread(target=record_audio)
    t2 = threading.Thread(target=recognize_audio)

    t_list = [t1, t2]

    for t in t_list:
        t.start()

    print("线程启动完毕")
    for t in t_list:
        t.join()
