from faster_whisper import WhisperModel
import srt
import pysrt
import moviepy.editor as mp
from moviepy.editor import VideoFileClip, AudioFileClip
import datetime
import pypinyin
from zhconv import convert
import pandas as pd
import os
import numpy as np
import shutil

video_match_list = [".mp4", ".avi"]

# whisper截取字幕
def save_srt(_media_path: str):
    _srt_save_path = os.path.join(data_save_dir, os.path.splitext(os.path.split(_media_path)[-1])[0] + ".srt")

    # 如果是视频文件, 则保存临时音频
    if os.path.splitext(_media_path)[-1] in video_match_list:
        temp_audio_path = "./temp_audio.mp3"

        video = mp.VideoFileClip(_media_path)
        audio = video.audio
        audio.write_audiofile(temp_audio_path)
        _media_path = temp_audio_path

        result = model.transcribe(_media_path, beam_size=5, word_timestamps=True)
        os.remove(temp_audio_path)
    else:
        result = model.transcribe(_media_path, beam_size=5, word_timestamps=True)

    segments, info = result
    print("语言预测为 '%s' ,概率是 %f" % (info.language, info.language_probability))

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

    # 保存SRT字幕文件
    srt_file = srt.compose(subtitles)

    with open(_srt_save_path, "w", encoding="utf-8") as f:
        f.write(srt_file)

    print("保存srt字幕: ", _srt_save_path)
    return _srt_save_path


# 判断一段拼音是否在文本中
def is_have_pinyin(judge_text: str, judge_word:str):
    data = pypinyin.lazy_pinyin(judge_text)
    sentence = " ".join(data)
    if judge_word in sentence:
        return True
    return False


# 获取包含某个发音的字段，对应的时间和文本信息, 比如使用judge_word="mu bei"
def get_text_time(srt_path, judge_word=None):
    subs = pysrt.open(srt_path, encoding='utf-8')

    audio_text_datas = []
    for sub in subs:
        start_time = sub.start.to_time()  # 字幕开始时间
        end_time = sub.end.to_time()  # 字幕结束时间
        start_ms = (
                           start_time.hour * 3600 + start_time.minute * 60 + start_time.second) * 1000 + start_time.microsecond // 1000
        end_ms = (end_time.hour * 3600 + end_time.minute * 60 + end_time.second) * 1000 + end_time.microsecond // 1000
        start_ms /= 1000
        end_ms /= 1000

        text = sub.text  # 字幕文本
        result = {"start": start_ms, "end": end_ms, "text": text}
        if judge_word is not None:
            if is_have_pinyin(text, judge_word):
                # 对时间和文本进行处理
                audio_text_datas.append(result)
            else:
                continue
        else:
            audio_text_datas.append(result)

    return audio_text_datas

# 根据字幕截取音频
def split_audio4srt(_media_path: str, _srt_save_path: str):
    if os.path.splitext(_media_path)[-1] in video_match_list:
        video = VideoFileClip(_media_path)
        audio = video.audio
    else:
        audio = AudioFileClip(_media_path)

    audio_text_datas = get_text_time(_srt_save_path, judge_word=None)

    # 开始剪切的对应的字幕和音频
    meta_data = []
    for i, data in enumerate(audio_text_datas):
        text: str
        start_time, end_time, text = data['start'], data['end'], data['text']

        print(data)
        # if "木杯" in text:
        #     text = text.replace('木杯', '墓碑')

        # 排除字数为1的音频
        if len(text) < 2:
            continue

        cut_audio = audio.subclip(start_time, end_time)

        audio_save_name = f"audio{i}.mp3"

        # 写入新的音频文件
        audio_file_save_path = os.path.join(audio_save_dir, audio_save_name)

        cut_audio.write_audiofile(audio_file_save_path)
        meta_data.append([audio_save_name, str(text)])
        # with open(info_file_save_path, "w", encoding="utf-8") as f:
        #     f.write(info)

        print(f"{i}: [{start_time}, {end_time}] : {text}")

    print(meta_data)
    meta_data = np.array(meta_data)
    meta_data = pd.DataFrame(meta_data, columns=['file_name', 'sentence'])
    print(meta_data)
    meta_data.to_csv(os.path.join(data_save_dir, "pre_metadata.csv"), encoding='utf-8', index=False)

    print('处理结束')




if __name__ == '__main__':
    # 数据路径
    media_path = r"D:\Code\ML\Video\card_video\2024_09_11 13_15_31.mp4"
    data_save_dir = r"D:\Code\ML\Audio\card_audio_data01"

    os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
    model_size = "medium"

    audio_save_dir = os.path.join(data_save_dir, "audio")
    model = WhisperModel(model_size, device="cuda", compute_type="float16")

    if not os.path.exists(audio_save_dir):
        os.makedirs(audio_save_dir)

    # 保存srt字幕
    srt_save_path = save_srt(media_path)

    # 切割音频数据, 生成训练数据
    split_audio4srt(media_path, srt_save_path)

