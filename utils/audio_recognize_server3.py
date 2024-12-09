import numpy as np
import websockets
import asyncio
from faster_whisper import WhisperModel
from zhconv import convert
import noisereduce as nr
import torch
import json
import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# 初始化 Whisper 模型
device = "cuda" if torch.cuda.is_available() else "cpu"
model_size = "deepdml/faster-whisper-large-v3-turbo-ct2"
model = WhisperModel(model_size, device=device, local_files_only=True)

# 音频窗口大小和步长
WINDOW_SIZE = 16000 * 3  # 3秒的音频
STEP_SIZE = 16000 * 1.5  # 每次滑动1.5秒

# 用于存储音频数据的缓冲区和上下文缓冲区
audio_buffer = np.array([], dtype=np.float32)
context_buffer = ""  # 上下文缓冲区，用于保持语义连贯
last_output = ""  # 上次完整输出的内容


# 降噪处理函数
def reduce_noise(audio_data):
    return nr.reduce_noise(y=audio_data, sr=16000)


async def handle_audio_stream(websocket, path):
    global audio_buffer, context_buffer, last_output

    try:
        async for message in websocket:
            # 接收音频数据并加入缓冲区
            audio_data = np.frombuffer(message, dtype=np.float32)
            audio_buffer = np.append(audio_buffer, audio_data)

            # 如果缓冲区达到窗口大小，进行语音识别
            while len(audio_buffer) >= WINDOW_SIZE:
                window_data = audio_buffer[:WINDOW_SIZE]
                audio_buffer = audio_buffer[int(STEP_SIZE):]  # 滑动窗口

                # 降噪处理
                clean_audio = reduce_noise(window_data)

                # 使用 Whisper 增量识别，启用时间戳和上下文
                segments, info = model.transcribe(clean_audio,
                                                  beam_size=1,
                                                  word_timestamps=True,
                                                  language='zh',
                                                  vad_filter=True,
                                                  vad_parameters=dict(min_silence_duration_ms=500),
                                                  initial_prompt=context_buffer)  # 使用上下文

                result = []
                last_end_time = 0.0
                current_sentence = ""

                # 根据时间戳分割句子
                for segment in segments:
                    for word in segment.words:
                        if word.start - last_end_time > 1.0:  # 两个词之间间隔超过1秒，认为是新句子
                            if current_sentence.strip():
                                result.append(current_sentence.strip())
                            current_sentence = word.word  # 开始新句子
                        else:
                            current_sentence += word.word
                        last_end_time = word.end

                # 将最后的未完成句子加入结果
                if current_sentence.strip():
                    result.append(current_sentence.strip())

                # 转换为简体中文
                result = [convert(sentence, 'zh-cn') for sentence in result]

                # 去除重复内容
                new_output = ""
                for sentence in result:
                    if sentence not in last_output:  # 仅添加新的内容
                        new_output += sentence
                last_output += new_output  # 更新上次输出内容

                # 更新上下文缓冲区
                context_buffer = result[-1] if result else context_buffer  # 使用最新的句子作为上下文

                # 输出识别结果
                if new_output.strip():
                    print(f"字幕更新: {new_output}")

                    # 将新的字幕发送回客户端
                    await websocket.send(json.dumps({"text": new_output}, ensure_ascii=False))

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        print("客户端断开连接")
        context_buffer = ""  # 清空上下文缓冲区
        last_output = ""  # 清空上次输出内容


# 启动 WebSocket 服务器
async def main():
    server = await websockets.serve(handle_audio_stream, "0.0.0.0", 2345)
    print("WebSocket 服务器已启动，监听端口 8765...")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
