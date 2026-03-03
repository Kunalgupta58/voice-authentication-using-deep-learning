import torch
import torch.nn as nn
import torch.nn.functional as F

class VoiceEmbeddingModel(nn.Module):
    def __init__(self):
        super(VoiceEmbeddingModel, self).__init__()

        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)

        self.fc1 = nn.Linear(32 * 10 * 31, 128)  # Adjusted after pooling
        self.dropout = nn.Dropout(0.3)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))

        x = torch.flatten(x, 1)
        x = self.dropout(self.fc1(x))

        # Normalize embedding
        x = F.normalize(x, p=2, dim=1)

        return x