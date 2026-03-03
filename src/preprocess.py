import librosa
import numpy as np

SAMPLE_RATE = 16000
DURATION = 4
FIXED_LENGTH = SAMPLE_RATE * DURATION  # 64000 samples

def load_audio(file_path):
    audio, sr = librosa.load(file_path, sr=SAMPLE_RATE)

    # Normalize audio
    audio = librosa.util.normalize(audio)

    # Pad or trim
    if len(audio) > FIXED_LENGTH:
        audio = audio[:FIXED_LENGTH]
    else:
        padding = FIXED_LENGTH - len(audio)
        audio = np.pad(audio, (0, padding))

    return audio

def extract_mfcc(audio):
    mfcc = librosa.feature.mfcc(
        y=audio,
        sr=SAMPLE_RATE,
        n_mfcc=40
    )

    return mfcc