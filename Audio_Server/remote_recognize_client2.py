import pyaudio
import numpy as np
import websockets
import asyncio

CHUNK = 16000 * 2  # 每次读取的音频数据大小
SERVER_URL = "ws://192.168.66.146:2345"  # WebSocket 服务器地址


async def record_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=CHUNK)

    # 连接到 WebSocket 服务器
    async with websockets.connect(SERVER_URL) as websocket:
        print("连接...")
        # frame = []
        while True:
            # for i in range(10):
            audio_data = stream.read(CHUNK)
                # frame.append(data)

            # audio_data = b''.join(frame)
            # frame = []
            audio_data = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            # 发送音频数据到服务器
            await websocket.send(audio_data.tobytes())

            # 接收服务器返回的识别结果
            response = await websocket.recv()
            print(f"识别结果: {response}")


# 启动客户端
async def main():
    await record_audio()


if __name__ == "__main__":
    asyncio.run(main())
