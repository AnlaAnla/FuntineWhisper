import pyaudio
import numpy as np
import websockets
import asyncio

CHUNK = 1600  # 每次读取的音频数据大小
SERVER_URL = "ws://192.168.66.146:2345"  # WebSocket 服务器地址


async def send_audio(websocket):
    """持续发送音频数据到服务器"""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=CHUNK)

    while True:
        data = stream.read(CHUNK)
        audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        await websocket.send(audio_data.tobytes())  # 发送音频数据


async def receive_results(websocket):
    """持续接收服务器返回的识别结果"""
    while True:
        response = await websocket.recv()  # 接收识别结果
        print(f"识别结果: {response}")


async def main():
    async with websockets.connect(SERVER_URL) as websocket:
        # 启动发送和接收任务
        await asyncio.gather(send_audio(websocket), receive_results(websocket))


if __name__ == "__main__":
    asyncio.run(main())
