from pytube import YouTube

# 输入YouTube视频链接
video_url = "https://www.youtube.com/watch?v=aGQIAA_sAs8"

# 创建YouTube对象
yt = YouTube(video_url)

# 获取视频标题
print(f"正在下载: {yt}")

# 获取视频的最高质量流
stream = yt.streams.get_audio_only()

# 下载视频
stream.download("./")

print("视频下载完成!")