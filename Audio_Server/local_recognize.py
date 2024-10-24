import pyaudio
import numpy as np
import wave
import time
from faster_whisper import WhisperModel
import torch
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = 'True'
