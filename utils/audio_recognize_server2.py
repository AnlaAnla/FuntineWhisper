from fastapi import FastAPI, WebSocket
from faster_whisper import WhisperModel
import torch
import numpy as np
from zhconv import convert
import uvicorn
import os
import noisereduce as nr
import asyncio
import json

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

app = FastAPI()
device = "cuda" if torch.cuda.is_available() else "cpu"
model_size = r"D:\Code\ML\Model\Whisper\checkpoint-100-2024Y_12M_04D_15h_24m_32s"
model = WhisperModel(model_size, device=device, local_files_only=True, cpu_threads=6, num_workers=4)


class AudioBuffer:
    def __init__(self, max_size=32000):  # 2秒的音频
        self.buffer = np.array([], dtype=np.float32)
        self.max_size = max_size

    def add_audio(self, audio_data):
        self.buffer = np.append(self.buffer, audio_data)
        if len(self.buffer) > self.max_size:
            self.buffer = self.buffer[-self.max_size:]

    def get_audio(self):
        return self.buffer.copy()

    def clear(self):
        self.buffer = np.array([], dtype=np.float32)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    audio_buffer = AudioBuffer()

    try:
        while True:
            data = await websocket.receive_bytes()
            audio_chunk = np.frombuffer(data, dtype=np.float32)

            # 添加音频数据到缓冲区
            audio_buffer.add_audio(audio_chunk)
            print(len(audio_buffer.buffer))

            # 当缓冲区达到一定大小时进行识别
            if len(audio_buffer.buffer) >= 4800:  # 1秒的音频
                audio_data = audio_buffer.get_audio()
                audio_buffer.clear()

                # 降噪
                audio_data = nr.reduce_noise(y=audio_data, sr=16000)

                # 识别
                segments, _ = model.transcribe(audio_data, beam_size=1, language="zh", vad_filter=True)
                text = ''.join([convert(segment.text, 'zh-cn') for segment in segments])

                if text.strip():  # 只有在有识别结果时才发送
                    print(text)
                    await websocket.send_json({"text": text})

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=2345)