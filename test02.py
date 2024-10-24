from moviepy.editor import VideoFileClip, AudioFileClip
import moviepy.editor as mp
import os

video = mp.VideoFileClip(r"C:\Code\ML\Video\t7.ts")
audio = video.audio
audio.write_audiofile(r"C:\Code\ML\Video\t7.mp3")
print('end')