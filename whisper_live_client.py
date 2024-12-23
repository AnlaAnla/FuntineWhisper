from whisper_live.client import TranscriptionClient

if __name__ == '__main__':
    client = TranscriptionClient(
        "192.168.31.146",
        2345,
        # lang="zh",
        # translate=False,
        # model="Systran/faster-whisper-small",  # also support hf_model => `Systran/faster-whisper-small`
        # use_vad=False,
        save_output_recording=True,  # Only used for microphone input, False by Default
        output_recording_filename="./output_recording.wav",  # Only used for microphone input
        max_clients=2,
        max_connection_time=36000
    )
    client()
