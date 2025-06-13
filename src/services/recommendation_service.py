# services/recommendation_service.py
import numpy as np
from typing import Dict, List
from sentence_transformers import SentenceTransformer
from db.models import Student, Project
from .model_loader import ModelLoader
import torch

class RecommendationService:
    def __init__(self, model_dir: str):
        self.model_loader = ModelLoader(model_dir)
        model_data = self.model_loader.load_model()
        
        self.model = model_data["model"]
        self.stack_vocab = model_data["stack_vocab"]
        self.roles_vocab = model_data["roles_vocab"]
        self.device = model_data["device"]
        
        # Инициализация sentence transformer
        self.text_model = SentenceTransformer(
            'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
            device=str(self.device))
    
    def _vectorize(self, items: List[str], vocab: Dict[str, int]) -> np.ndarray:
        """Преобразует список элементов в вектор с использованием словаря"""
        vec = np.zeros(len(vocab))
        for item in items:
            if item in vocab:
                vec[vocab[item]] = 1
        return vec
    
    async def predict_for_student(self, student: Student, projects: List[Project]) -> Dict[int, float]:
        # Преобразование стека студента
        student_stack = student.stack.split(',') if student.stack else []
        student_stack_vec = self._vectorize(student_stack, self.stack_vocab)
        
        # Преобразование ролей студента
        student_roles = student.desired_role.split(',') if student.desired_role else []
        student_roles_vec = self._vectorize(student_roles, self.roles_vocab)
        
        # Объединение признаков студента
        student_features = np.hstack([student_stack_vec, student_roles_vec])
        student_features = torch.FloatTensor(student_features).to(self.device)
        
        # Обработка проектов
        project_features = []
        for project in projects:
            # Стек проекта
            project_stack = project.stack.split(',') if project.stack else []
            stack_vec = self._vectorize(project_stack, self.stack_vocab)
            
            # Роли проекта
            project_roles = project.required_roles.split(',') if project.required_roles else []
            roles_vec = self._vectorize(project_roles, self.roles_vocab)
            
            # Описание проекта
            desc_vec = self.text_model.encode(
                project.description if project.description else "",
                convert_to_tensor=True,
                device=self.device)
            
            # Объединение признаков проекта
            features = np.hstack([
                stack_vec,
                roles_vec,
                desc_vec.cpu().numpy()
            ])
            project_features.append(features)
        
        project_features = torch.FloatTensor(np.vstack(project_features)).to(self.device)
        
        with torch.no_grad():
            student_features_expanded = student_features.unsqueeze(0).repeat(len(projects), 1)
            scores = self.model(student_features_expanded, project_features)
            
        return {p.id: score.item() for p, score in zip(projects, scores)}