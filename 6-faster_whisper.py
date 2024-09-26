from datetime import datetime

import whisper
from faster_whisper import WhisperModel
import srt
import moviepy.editor as mp
import datetime
from zhconv import convert
import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
video_match_list = [".mp4", ".avi"]


def media2text(_media_path: str):
    # 如果是视频文件, 则保存临时音频
    if os.path.splitext(_media_path)[-1] in video_match_list:
        temp_audio_path = "./temp_audio.mp3"

        video = mp.VideoFileClip(_media_path)
        audio = video.audio
        audio.write_audiofile(temp_audio_path)
        _media_path = temp_audio_path

        _result = model.transcribe(_media_path, beam_size=5, word_timestamps=True)
        os.remove(temp_audio_path)
    else:
        _result = model.transcribe(_media_path, beam_size=5, word_timestamps=True)

    return _result


# srt文件格式为 *.srt
def result2srt(result, srt_save_path=None):
    segments, info = result

    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    # 创建SRT字幕文件
    subtitles = []
    # start_time = datetime.timedelta()

    for segment in segments:
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
        text = segment.text.strip()
        text = convert(text, 'zh-cn')
        if text:
            start_time = datetime.timedelta(seconds=segment.start)
            end_time = datetime.timedelta(seconds=segment.end)
            subtitles.append(
                srt.Subtitle(
                    index=len(subtitles) + 1,
                    start=start_time,
                    end=end_time,
                    content=text,
                )
            )

    if srt_save_path is not None:
        # 保存SRT字幕文件
        srt_file = srt.compose(subtitles)
        with open(srt_save_path, "w", encoding="utf-8") as f:
            f.write(srt_file)

        print("保存srt字幕")


if __name__ == '__main__':
    model_path = "models/whisper-medium-finetune-ct2"
    media_path = r"D:\Code\ML\Video\merged_video.ts"

    # Run on GPU with FP16
    model = WhisperModel(model_path, device="cuda", compute_type="float16")

    result = media2text(media_path)
    result2srt(result)
