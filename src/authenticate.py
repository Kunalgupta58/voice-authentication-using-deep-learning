import torch
import numpy as np
import os
from model import VoiceEmbeddingModel
from preprocess import load_audio, extract_mfcc
import torch.nn.functional as F

# Load trained model

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "embedding_model.pth")

model = VoiceEmbeddingModel()
model.load_state_dict(torch.load(model_path))
model.eval()

# Enrollment function
def enroll(file_path):
    audio = load_audio(file_path)
    mfcc = extract_mfcc(audio)
    mfcc = np.expand_dims(mfcc, axis=0)
    mfcc = np.expand_dims(mfcc, axis=0)

    mfcc_tensor = torch.tensor(mfcc, dtype=torch.float32)

    with torch.no_grad():
        embedding = model(mfcc_tensor)

    return embedding


# Authentication function
def authenticate(enrolled_embedding, test_file_path, threshold=0.75):
    audio = load_audio(test_file_path)
    mfcc = extract_mfcc(audio)
    mfcc = np.expand_dims(mfcc, axis=0)
    mfcc = np.expand_dims(mfcc, axis=0)

    mfcc_tensor = torch.tensor(mfcc, dtype=torch.float32)

    with torch.no_grad():
        test_embedding = model(mfcc_tensor)

    similarity = F.cosine_similarity(enrolled_embedding, test_embedding)

    print("Similarity Score:", similarity.item())

    if similarity.item() > threshold:
        print("Authentication Successful")
    else:
        print("Authentication Failed")


if __name__ == "__main__":
    # Use absolute paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    audio_path_1 = os.path.join(base_dir, "dataset/raw_audio/anshi/anshi 1.wav")
    audio_path_2 = os.path.join(base_dir, "dataset/raw_audio/anshi/anshi 2.wav")
    enrolled = enroll(audio_path_1)
    authenticate(enrolled, audio_path_2)