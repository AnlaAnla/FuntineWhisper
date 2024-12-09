import pyaudio
import numpy as np
import websockets
import asyncio

CHUNK = 3200  # 每次读取的音频块大小
SERVER_URL = "ws://192.168.66.146:2345"  # WebSocket 服务器地址


async def audio_producer(websocket):
    """读取音频数据并发送到服务器"""
    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        frames_per_buffer=CHUNK)

        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32)

            print(np.max(audio_data))
            if np.max(audio_data) > 1000:
                await websocket.send(audio_data.tobytes())
            # print(f"发送音频块大小: {len(audio_data.tobytes())}")

    except websockets.exceptions.ConnectionClosed as e:
        print(f"连接关闭: {e}")
    except Exception as e:
        print(f"音频读取错误: {e}")


async def receive_results(websocket):
    """接收服务器返回的识别结果"""
    while True:
        try:
            response = await websocket.recv()
            print(f"识别结果: {response}")
        except websockets.exceptions.ConnectionClosed as e:
            print(f"连接关闭: {e}")
            break


async def main():
    async with websockets.connect(SERVER_URL) as websocket:
        audio_task = asyncio.create_task(audio_producer(websocket))
        receiver_task = asyncio.create_task(receive_results(websocket))

        await asyncio.gather(audio_task, receiver_task)


if __name__ == "__main__":
    asyncio.run(main())
