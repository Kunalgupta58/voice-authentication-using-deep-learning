import os
import numpy as np
from preprocess import load_audio, extract_mfcc

DATA_PATH = "../dataset/raw_audio"

features = []
labels = []

for speaker in os.listdir(DATA_PATH):
    speaker_path = os.path.join(DATA_PATH, speaker)

    for file in os.listdir(speaker_path):
        if file.endswith(".wav"):
            file_path = os.path.join(speaker_path, file)

            audio = load_audio(file_path)
            mfcc = extract_mfcc(audio)

            features.append(mfcc)
            labels.append(speaker)

features = np.array(features)
labels = np.array(labels)

np.save("features.npy", features)
np.save("labels.npy", labels)

print("Dataset created successfully!")
print("Features shape:", features.shape)