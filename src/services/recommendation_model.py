import torch
import torch.nn as nn
import torch.nn.functional as F
class TwoTowerModel(nn.Module):
    def __init__(self, student_feature_dim: int, project_feature_dim: int, embedding_dim: int = 128):
        super().__init__()
        self.s_tower = nn.Sequential(
            nn.Linear(student_feature_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, embedding_dim)
        )

        self.p_tower = nn.Sequential(
            nn.Linear(project_feature_dim, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, embedding_dim)
        )

    def forward(self, student_features: torch.Tensor, project_features: torch.Tensor) -> torch.Tensor:
        student_embedding = self.s_tower(student_features)
        project_embedding = self.p_tower(project_features)
        similarity = F.cosine_similarity(student_embedding, project_embedding, dim=1)
        return similarity
