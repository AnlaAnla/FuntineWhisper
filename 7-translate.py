from faster_whisper import WhisperModel
import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


model = WhisperModel("medium")
text_to_translate = "Hello, how are you?"
segments, info = model.transcribe(r"D:\Code\ML\Audio\t7.mp3", task="translate", language="zh")

print(info)
for segment in segments:
    print(segment)