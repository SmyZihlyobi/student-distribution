from typing import Dict, List
from .recommendation_service import RecommendationService
from db.project_repository import ProjectRepository
from db.student_repository import StudentRepository

class RecommendationEngine:
    def __init__(self, model_service: RecommendationService):
        self.model_service = model_service

    async def get_recommendations(
        self,
        student_id: int,
        student_repo: StudentRepository,
        project_repo: ProjectRepository,
        top_n: int = 5
    ) -> List[Dict]:
        """Получение рекомендаций для студента"""
        student = await student_repo.get_student_by_id(student_id=student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")


        projects = await project_repo.get_active_projects()
        scores = await self.model_service.predict_for_student(student, projects)

        sorted_projects = sorted(
            [(p, scores[p.id]) for p in projects],
            key=lambda x: x[1],
            reverse=True
        )[:top_n]

        return [{
            "project_id": p.id,
            "project_name": p.name,
            "match_score": round(score, 4),
            "required_stack": p.stack,
            "required_roles": p.required_roles
        } for p, score in sorted_projects]