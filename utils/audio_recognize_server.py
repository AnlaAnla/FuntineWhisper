from fastapi import FastAPI, UploadFile, File
from faster_whisper import WhisperModel
import torch
import numpy as np
from zhconv import convert
import uvicorn
import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

app = FastAPI()

# 加载模型
device = "cuda" if torch.cuda.is_available() else "cpu"
model = WhisperModel("medium", device=device, local_files_only=True)


@app.post("/recognize_audio/")
async def recognize_audio(file: UploadFile = File(...)):
    audio_data = await file.read()
    audio_data = np.frombuffer(audio_data, dtype=np.float32)

    # 进行语音识别
    segments, info = model.transcribe(audio_data, beam_size=5, language="zh", vad_filter=True,
                                      vad_parameters=dict(min_silence_duration_ms=500))

    # 拼接识别的文字
    paragraph = ''
    if segments:
        for segment in segments:
            text = convert(segment.text, 'zh-cn')
            paragraph += text

    print(' ---: ', paragraph)
    return {"text": paragraph}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=2345)
