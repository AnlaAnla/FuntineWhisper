import numpy as np
import websockets
import asyncio
from faster_whisper import WhisperModel
from zhconv import convert
from collections import deque
import torch
import json
import noisereduce as nr
import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# 初始化 Whisper 模型
device = "cuda" if torch.cuda.is_available() else "cpu"
model_size = "deepdml/faster-whisper-large-v3-turbo-ct2"
model = WhisperModel(model_size, device=device, local_files_only=True)

# 全局配置
BUFFER_SIZE = 16000  # 1 秒音频
last_processed_time = 0.0
context_buffer = ""  # 上下文缓冲区
MAX_CONTEXT_LENGTH = 100  # 上下文最大长度


class WhisperServer:
    def __init__(self):
        self.context_buffer = ""
        self.model = WhisperModel(model_size, device=device, local_files_only=True)

    def update_context(self, current_context, new_content):
        current_context += new_content
        if len(current_context) > MAX_CONTEXT_LENGTH:
            current_context = current_context[-MAX_CONTEXT_LENGTH:]
        return current_context

    async def handle_audio_stream(self, websocket, path):
        buffer = deque(maxlen=BUFFER_SIZE)

        try:
            async for message in websocket:
                audio_data = np.frombuffer(message, dtype=np.float32)/32768.0
                buffer.extend(audio_data)

                if len(buffer) == BUFFER_SIZE:
                    clean_audio = nr.reduce_noise(y=np.array(buffer), sr=16000, prop_decrease=0.8)
                    segments, _ = self.model.transcribe(
                        clean_audio,
                        beam_size=1,
                        word_timestamps=False,
                        language='zh',
                        vad_filter=True,
                        vad_parameters=dict(min_silence_duration_ms=500),
                        initial_prompt=self.context_buffer
                    )

                    new_output = ''
                    if segments:
                        for segment in segments:
                            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
                            text = convert(segment.text, 'zh-cn')
                            new_output += f" {text}"

                    if new_output.strip():
                        current_output = new_output
                        self.context_buffer = self.update_context(self.context_buffer, current_output)
                        print(current_output)
                        await websocket.send(json.dumps({"text": current_output}, ensure_ascii=False))

        except Exception as e:
            print(f"发生错误: {e}")
        finally:
            print("客户端断开连接")


# 启动 WebSocket 服务器
async def main():
    server = WhisperServer()
    await websockets.serve(server.handle_audio_stream, "0.0.0.0", 2345)
    print("WebSocket 服务器已启动，监听端口 2345...")
    await asyncio.Future()  # 保持服务器运行


if __name__ == "__main__":
    asyncio.run(main())