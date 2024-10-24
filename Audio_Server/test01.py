import pyaudio
import numpy as np
import wave
import time
from faster_whisper import WhisperModel
import torch
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = 'True'

CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # 录音时的采样率

temp_time = time.time()


def whisper_audio(audio_data, model):
    segments, info = model.transcribe(audio_data, beam_size=5, language="zh", vad_filter=True,
                                      vad_parameters=dict(min_silence_duration_ms=500))
    # print(f"{filename} removed.")
    if segments:
        print('text:')
        for segment in segments:
            print(segment.text, end=' ')
        print()
    # t2 = time.time()
    # print("推理时间: ", t2 - t1)
    # global temp_time
    # print("从记录到间隔: ", t2 - temp_time)


def write_audio(WAVE_OUTPUT_FILENAME, p, frame):
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frame))
    wf.close()


def Monitor_MIC(th, filename):
    space_num = 0
    WAVE_OUTPUT_FILENAME = filename + ".mp3"

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    frames = []
    while (True):
        print("ready for recording" + str(time.localtime(time.time()).tm_sec))
        for i in range(0, 30):
            data = stream.read(CHUNK)
            frames.append(data)
        audio_data = np.frombuffer(data, dtype=np.int16)
        temp = np.max(audio_data)
        # print(f'temp 大小为:[{np.min(audio_data)}, {temp}]')
        if temp > th:
            print("detected a signal")
            print('current threshold：', temp)
            less = []
            frames2 = []
            while True:
                # print("recording")
                global temp_time
                temp_time = time.time()

                for i in range(0, 5):
                    data2 = stream.read(CHUNK)
                    frames2.append(data2)
                audio_data2 = np.frombuffer(data2, dtype=np.int16)
                temp2 = np.max(audio_data2)

                # print(f'temp2 大小为:[{np.min(audio_data2)}, {temp2}]')
                if temp2 < th:
                    less.append(-1)
                    print("below threshold, counting: ", less)
                    # 如果有连续15个循环的点，都不是声音信号，就认为音频结束了
                    if len(less) == 1:
                        # audio_name = f"{space_num}.mp3"
                        # audio_name = "temp.mp3"
                        # write_audio(audio_name, p, frames2)
                        # print('写入: ', audio_name)
                        space_num += 1
                        # frames2 = []

                        audio_data = b''.join(frames2)
                        audio_data = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

                        whisper_audio(audio_data, model)

                    elif len(less) == 8:
                        frames2 = []
                        print("===================")

                    elif len(less) == 30:
                        break
                else:
                    less = []
            break

    print("间断次数: ", space_num)
    stream.stop_stream()
    stream.close()
    p.terminate()


if __name__ == '__main__':
    print("Loading model...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using {device} device.")
    model = WhisperModel("base", device=device, local_files_only=True,
                         compute_type="int8")

    print("Model loaded.")

    Monitor_MIC(th=200, filename='tt1')
