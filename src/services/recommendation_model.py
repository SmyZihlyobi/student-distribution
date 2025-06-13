import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from db.models import Student, Project

class TwoTowerModel(nn.Module):
    def __init__(self, student_feature_dim: int, project_feature_dim: int, embedding_dim: int = 128):
        super().__init__()
        self.student_tower = nn.Sequential(
            nn.Linear(student_feature_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, embedding_dim)
        )
        self.project_tower = nn.Sequential(
            nn.Linear(project_feature_dim, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, embedding_dim)
        )

    def forward(self, student_features: torch.Tensor, project_features: torch.Tensor) -> torch.Tensor:
        student_embedding = self.student_tower(student_features)
        project_embedding = self.project_tower(project_features)
        return F.cosine_similarity(student_embedding, project_embedding, dim=1)

import torch
import numpy as np
from typing import Dict, List
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from db.models import Student, Project

class TwoTowerModel(torch.nn.Module):
    def __init__(self, student_dim: int, project_dim: int):
        super().__init__()
        self.student_tower = torch.nn.Linear(student_dim, 128)
        self.project_tower = torch.nn.Linear(project_dim, 128)
        
    def forward(self, student_features, project_features):
        student_emb = self.student_tower(student_features)
        project_emb = self.project_tower(project_features)
        return torch.nn.functional.cosine_similarity(student_emb, project_emb)

class RecommendationService:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.text_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        self.stack_vectorizer = TfidfVectorizer()
        self.role_vectorizer = TfidfVectorizer()
        self.model = None
        
    async def init_model(self, projects: List[Project]):
        """Инициализация модели с предобработкой данных проектов"""
        all_stacks = [p.stack for p in projects if p.stack]
        all_roles = [p.required_roles for p in projects if p.required_roles]
        
        self.stack_vectorizer.fit(all_stacks)
        self.role_vectorizer.fit(all_roles)
        
        student_dim = len(self.stack_vectorizer.vocabulary_) + len(self.role_vectorizer.vocabulary_)
        project_dim = student_dim + self.text_model.get_sentence_embedding_dimension()
        self.model = TwoTowerModel(student_dim, project_dim).to(self.device)
        
    async def predict_for_student(self, student: Student, projects: List[Project]) -> Dict[int, float]:
        """Получение предсказаний для конкретного студента"""
        if not self.model:
            raise RuntimeError("Model not initialized. Call init_model first.")
            
        student_stack_vec = self.stack_vectorizer.transform([student.stack or ""])
        student_role_vec = self.role_vectorizer.transform([student.desired_role or ""])
        student_features = torch.FloatTensor(
            np.hstack([student_stack_vec.toarray(), student_role_vec.toarray()])
        ).to(self.device)
        
        project_features = []
        for project in projects:
            stack_vec = self.stack_vectorizer.transform([project.stack or ""])
            role_vec = self.role_vectorizer.transform([project.required_roles or ""])
            desc_vec = self.text_model.encode(project.description)
            features = np.hstack([
                stack_vec.toarray(),
                role_vec.toarray(),
                desc_vec.reshape(1, -1)
            ])
            project_features.append(features)
            
        project_features = torch.FloatTensor(np.vstack(project_features)).to(self.device)
        
        with torch.no_grad():
            student_features_expanded = student_features.repeat(len(projects), 1)
            scores = self.model(student_features_expanded, project_features)
            
        return {p.id: score.item() for p, score in zip(projects, scores)}