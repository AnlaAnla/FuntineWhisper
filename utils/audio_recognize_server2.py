import numpy as np
import websockets
import asyncio
import webrtcvad
from zhconv import convert
from faster_whisper import WhisperModel
import torch
import json
import os
import noisereduce as nr

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# 初始化 Whisper 模型
device = "cuda" if torch.cuda.is_available() else "cpu"
model_size = "deepdml/faster-whisper-large-v3-turbo-ct2"
model = WhisperModel(model_size, device=device, local_files_only=True)

# 初始化 VAD
vad = webrtcvad.Vad(3)  # 设置为最严格模式

# 音频窗口大小和步长（调整为每 2 秒）
WINDOW_SIZE = 16000 * 2  # 2秒的音频
STEP_SIZE = 16000  # 每次滑动1秒

# 用于存储音频数据的缓冲区
audio_buffer = np.array([], dtype=np.int16)


def reduce_noise(audio_data):
    reduced_audio = nr.reduce_noise(y=audio_data, sr=16000)
    return reduced_audio


async def handle_audio_stream(websocket, path):
    global audio_buffer

    try:
        async for message in websocket:
            audio_data = np.frombuffer(message, dtype=np.float32)

            # 降噪处理
            audio_data = reduce_noise(audio_data)

            # 将音频数据加入缓冲区
            audio_buffer = np.append(audio_buffer, audio_data)

            # 滑动窗口处理
            while len(audio_buffer) >= WINDOW_SIZE:
                window_data = audio_buffer[:WINDOW_SIZE]
                audio_buffer = audio_buffer[STEP_SIZE:]  # 移动窗口，去除已识别的部分

                # # 对窗口数据进行 VAD 判断，检测是否为语音
                # if vad.is_speech(window_data.tobytes(), 16000):
                # 使用 Whisper 模型进行语音识别

                segments, info = model.transcribe(window_data, beam_size=5, language="zh", vad_filter=True)
                result = "".join([segment.text for segment in segments])
                result = convert(result, 'zh-cn')

                print(f"识别结果: {result}")
                # 将识别结果发送回客户端
                await websocket.send(json.dumps({"text": result}, ensure_ascii=False))

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        print("客户端断开连接")


# 启动 WebSocket 服务器
async def main():
    server = await websockets.serve(handle_audio_stream, "0.0.0.0", 2345)
    print("WebSocket 服务器已启动，监听端口 2345...")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
