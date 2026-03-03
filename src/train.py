import torch
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from model import VoiceEmbeddingModel
import torch.nn as nn
import torch.optim as optim

# Load data
import os
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))

features_path = os.path.join(current_dir, "features.npy")
labels_path = os.path.join(current_dir, "labels.npy")

features = np.load(features_path)
labels = np.load(labels_path)

# Add channel dimension for CNN
features = np.expand_dims(features, axis=1)

# Encode labels
encoder = LabelEncoder()
labels = encoder.fit_transform(labels)

X_train, X_test, y_train, y_test = train_test_split(
    features, labels, test_size=0.2, random_state=42
)

X_train = torch.tensor(X_train, dtype=torch.float32)
y_train = torch.tensor(y_train, dtype=torch.long)

X_test = torch.tensor(X_test, dtype=torch.float32)
y_test = torch.tensor(y_test, dtype=torch.long)

model = VoiceEmbeddingModel()

classifier = nn.Linear(128, len(set(labels)))

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(list(model.parameters()) + list(classifier.parameters()), lr=0.001)

for epoch in range(50):
    embeddings = model(X_train)
    outputs = classifier(embeddings)

    loss = criterion(outputs, y_train)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if epoch % 10 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item()}")

# Save model
model_save_path = os.path.join(current_dir, "embedding_model.pth")
torch.save(model.state_dict(), model_save_path)

print("Training complete!")