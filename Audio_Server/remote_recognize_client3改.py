import pyaudio
import numpy as np
import websockets
import asyncio

CHUNK = 3200  # 每次读取的音频数据大小，对应 0.2 秒
SERVER_URL = "ws://192.168.66.146:2345"  # WebSocket 服务器地址


async def send_audio(websocket, audio_queue):
    """持续读取音频数据并发送到服务器"""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=CHUNK)

    while True:
        data = stream.read(CHUNK)
        audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
        await audio_queue.put(audio_data.tobytes())  # 将音频数据放入队列


async def audio_sender(websocket, audio_queue):
    """从队列中获取音频数据并发送到服务器"""
    while True:
        audio_data = await audio_queue.get()
        await websocket.send(audio_data)  # 发送音频数据


async def receive_results(websocket):
    """持续接收服务器返回的识别结果"""
    while True:
        try:
            response = await websocket.recv()  # 接收识别结果
            print(f"识别结果: {response}")
        except websockets.exceptions.ConnectionClosed as e:
            print(f"连接关闭: {e}")
            break


async def main():
    async with websockets.connect(SERVER_URL) as websocket:
        audio_queue = asyncio.Queue()

        # 启动音频读取和发送任务
        audio_task = asyncio.create_task(send_audio(websocket, audio_queue))
        sender_task = asyncio.create_task(audio_sender(websocket, audio_queue))

        # 启动接收任务
        receiver_task = asyncio.create_task(receive_results(websocket))

        await asyncio.gather(audio_task, sender_task, receiver_task)


if __name__ == "__main__":
    asyncio.run(main())
