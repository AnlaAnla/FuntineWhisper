import time
import wave
import pyaudio
import numpy as np
import queue
import threading
import asyncio
import websockets

CHUNK = 9600
AUDIO_THRESHOLD = 1000  # 音频检测阈值
SERVER_URL = "ws://192.168.66.146:2345/ws/audio_stream"  # WebSocket 服务器地址

# 初始化音频流
p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=CHUNK
)


def write_audio(WAVE_OUTPUT_FILENAME, audio_data):
    """保存音频数据到文件"""
    audio_data = (audio_data * 32768.0).astype(np.int16)

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    wf.setframerate(16000)
    wf.writeframes(audio_data.tobytes())
    wf.close()


def record_audio(audio_queue, stop_event):
    """录制音频并检测阈值"""
    while not stop_event.is_set():
        data = stream.read(CHUNK)
        audio_data = np.frombuffer(data, dtype=np.int16)
        if np.max(audio_data) > AUDIO_THRESHOLD:
            # print("检测到音频，开始录制")
            while True:
                audio_queue.put(audio_data)
                data = stream.read(CHUNK)
                audio_data = np.frombuffer(data, dtype=np.int16)
                if np.max(audio_data) < AUDIO_THRESHOLD:
                    break


async def send_audio_to_server(audio_queue, stop_event):
    """将音频数据实时发送到服务器并接收识别结果"""
    async with websockets.connect(SERVER_URL) as websocket:
        try:
            while not stop_event.is_set():
                if not audio_queue.empty():
                    audio_chunk = audio_queue.get().astype(np.float32) / 32768.0

                    await websocket.send(audio_chunk.tobytes())  # 发送音频数据
                    response = await websocket.recv()  # 接收识别结果
                    # print(f"\r识别结果: {response}", end="")
                    print(response, end='')
        except websockets.ConnectionClosed:
            print("\n连接关闭")
        except Exception as e:
            print(f"\n发生错误: {e}")


def main():
    audio_queue = queue.Queue()
    stop_event = threading.Event()

    # 启动音频录制线程
    record_thread = threading.Thread(target=record_audio, args=(audio_queue, stop_event))
    record_thread.start()

    # 启动音频发送和识别任务
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(send_audio_to_server(audio_queue, stop_event))
    except KeyboardInterrupt:
        print("\n停止客户端")
        stop_event.set()
        record_thread.join()


if __name__ == '__main__':
    main()
