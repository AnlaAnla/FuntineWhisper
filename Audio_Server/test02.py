import queue
import threading
import tempfile
import wave
import os
from pydub import AudioSegment
import pyaudio
import numpy as np
from faster_whisper import WhisperModel

os.environ["KMP_DUPLICATE_LIB_OK"] = 'True'

# 初始化Whisper模型
model = WhisperModel("base", device="cpu")

# 初始化PyAudio
audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=1024)

# 创建临时文件
temp_dir = tempfile.gettempdir()
temp_file = os.path.join(temp_dir, 'temp.mp3')

# 音频缓冲队列
q = queue.Queue()

CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # 录音时的采样率



def write_audio(WAVE_OUTPUT_FILENAME, p, frame):
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frame))
    wf.close()


# 音频写入线程
def audio_writer_thread():
    frames = []
    while True:
        data = q.get()
        if data is None:
            break
        frames.append(data)
        if len(frames) >= 5:  # 当有足够的数据时
            frames.append(data)
            print("写入:", temp_file)
            write_audio(temp_file, audio, frames)
            frames = []


# 语音识别线程
def speech_recognition_thread():
    while True:
        if os.path.exists(temp_file):
            try:
                print('预测')
                segments, info = model.transcribe(temp_file, beam_size=5, language="zh", vad_filter=True,
                                                  vad_parameters=dict(min_silence_duration_ms=500),
                                                  streaming=True)
                if segments:
                    for segment in segments:
                        print(segment)
            except:
                pass


# 音频采集线程
def audio_capture_thread():
    while True:
        data = stream.read(1024)
        q.put(data)



if __name__ == '__main__':

    # 启动线程
    threading.Thread(target=audio_writer_thread, daemon=True).start()
    threading.Thread(target=speech_recognition_thread, daemon=True).start()
    threading.Thread(target=audio_capture_thread, daemon=True).start()
    print('启动')
    # 保持主线程运行
    while True:
        try:
            pass
        except KeyboardInterrupt:
            q.put(None)  # 发送结束信号
            break
