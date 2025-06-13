import numpy as np
import torch
import torch.nn.functional as F
from typing import Dict, List
from sentence_transformers import SentenceTransformer
from db.models import Student, Project
from .model_loader import ModelLoader
from .recommendation_model import TwoTowerModel

def parse_string(string: str | List[str]) -> List[str]:
    """Преобразует строку в список, разделяя по запятой"""
    if isinstance(string, list):
        return [term.lower() for term in string]
    
    return string.lower().split(', ')

class RecommendationService:
    def __init__(self, model_dir: str):
        self.model_loader = ModelLoader(model_dir)
        model_data = self.model_loader.load_model()

        self.model: TwoTowerModel = model_data["model"]
        self.stack_vocab: Dict[str, int] = model_data["stack_vocab"]
        self.roles_vocab: Dict[str, int] = model_data["roles_vocab"]
        self.device = model_data["device"]

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

    def _vectorize_student(self, student: Student, stack_vocab: Dict[str, int], roles_vocab: Dict[str, int]) -> np.ndarray:
        if not student.stack or not student.desired_role:
            raise ValueError("Student stack or desired role is missing.")

        student_stack = parse_string(student.stack)
        student_desired_role = parse_string(student.desired_role)

        stack_vec = self._vectorize(student_stack, stack_vocab)
        roles_vec = self._vectorize(student_desired_role, roles_vocab)
        return np.concatenate([stack_vec, roles_vec])

    def _vectorize_project(self, project: Project, stack_vocab: Dict[str, int], roles_vocab: Dict[str, int], text_model: SentenceTransformer) -> np.ndarray:
        if not project.stack or not project.required_roles or not project.description:
            raise ValueError("Project stack, required roles, or description is missing.")

        project_stack = parse_string(project.stack)
        roles = parse_string(project.required_roles)
        
        stack_vec = self._vectorize(project_stack, stack_vocab)
        roles_vec = self._vectorize(roles, roles_vocab)
        text_embedding = text_model.encode(project.description, convert_to_numpy=True)
        return np.concatenate([stack_vec, roles_vec, text_embedding])

    async def predict_for_student(self, student: Student, projects: List[Project]) -> Dict[int, float]:
        """Предсказывает релевантность проектов для студента"""
        if not self.model:
            raise RuntimeError("Model not loaded.")

        student_features = self._vectorize_student(student, self.stack_vocab, self.roles_vocab)
        student_features_tensor = torch.tensor(student_features, dtype=torch.float32).unsqueeze(0).to(self.device)

        scores: Dict[int, float] = {}
        for project in projects:
            project_features = self._vectorize_project(project, self.stack_vocab, self.roles_vocab, self.text_model)
            project_features_tensor = torch.tensor(project_features, dtype=torch.float32).unsqueeze(0).to(self.device)

            with torch.no_grad():
                student_embedding = self.model.s_tower(student_features_tensor)
                project_embedding = self.model.p_tower(project_features_tensor)
                similarity = F.cosine_similarity(student_embedding, project_embedding, dim=1).item()

            scores[project.id] = similarity

        return scores