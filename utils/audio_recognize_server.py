from fastapi import FastAPI, UploadFile, File
from faster_whisper import WhisperModel
import torch
import numpy as np
from zhconv import convert
import uvicorn
import os
import noisereduce as nr

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

app = FastAPI()

# 加载模型
device = "cuda" if torch.cuda.is_available() else "cpu"

model_size = r"D:\Code\ML\Model\Whisper\checkpoint-100-2024Y_12M_04D_15h_24m_32s"
# model_size = "deepdml/faster-whisper-large-v3-turbo-ct2"
# model_size = "medium"

model = WhisperModel(model_size, device=device, local_files_only=True, cpu_threads=6, num_workers=4)


def reduce_noise(audio_data):
    reduced_audio = nr.reduce_noise(y=audio_data, sr=16000)
    return reduced_audio


@app.post("/recognize_audio/")
async def recognize_audio(file: UploadFile = File(...)):

    audio_data = await file.read()
    audio_data = np.frombuffer(audio_data, dtype=np.float32)

    # 降噪处理
    audio_data = reduce_noise(audio_data)

    # 进行语音识别
    segments, info = model.transcribe(audio_data,
                                      beam_size=1,
                                      language="zh",
                                      # language=None,
                                      vad_filter=True,
                                      vad_parameters=dict(min_silence_duration_ms=500)
                                      )
    # segments, info = model.transcribe(audio_data, beam_size=5, language="zh",
    #                                   vad_filter=True)

    # 拼接识别的文字
    paragraph = ''
    if segments:
        for segment in segments:
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
            text = convert(segment.text, 'zh-cn')
            paragraph += f" {text}"

    global total_num
    total_num += 1
    print(f' --[{total_num}]--: {paragraph}')
    return {"text": paragraph}


if __name__ == "__main__":
    total_num = 0
    uvicorn.run(app, host="0.0.0.0", port=2345)
