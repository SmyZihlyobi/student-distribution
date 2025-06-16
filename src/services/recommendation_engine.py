from typing import Dict, List, Union # Or just List, Dict if Python 3.9+
from .recommendation_service import RecommendationService, parse_string
from db.project_repository import ProjectRepository
from db.student_repository import StudentRepository
from db.models import Student, Project # For type hinting

class RecommendationEngine:
    def __init__(self, model_service: RecommendationService):
        self.model_service = model_service

    async def get_recommendations(
        self,
        student_id: int,
        student_repo: StudentRepository,
        project_repo: ProjectRepository,
        top_n: int = 5,
        bonus_per_match: float = 0.05
    ) -> List[Dict]:
        student = await student_repo.get_student_by_id(student_id=student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")

        if not student.stack:
            raise ValueError(f"Student {student_id} has no stack information.")


        student_stack_list = parse_string(student.stack)
        student_stack_set = set(student_stack_list)

        projects = await project_repo.get_active_projects()
        if not projects:
            return []

        scores = await self.model_service.predict_for_student(student, projects)

        project_score_pairs = []
        for p in projects:
            if p.id in scores:
                project_score_pairs.append((p, scores[p.id]))

        if not project_score_pairs:
            return []

        candidate_count = min(top_n * 3, len(project_score_pairs))

        sorted_initial_candidates = sorted(
            project_score_pairs,
            key=lambda x: x[1],
            reverse=True
        )[:candidate_count]

        processed_candidates = []
        for project_obj, base_similarity in sorted_initial_candidates:
            project_stack_list = []
            if project_obj.stack:
                project_stack_list = parse_string(project_obj.stack)
            project_stack_set = set(project_stack_list)

            matches = student_stack_set.intersection(project_stack_set)
            bonus = len(matches) * bonus_per_match
            final_s = base_similarity + bonus

            processed_candidates.append({
                "project_id": project_obj.id,
                "project_name": project_obj.name,
                "final_score": final_s,
                "base_similarity": base_similarity,
                "bonus_score": bonus,
                "required_stack": project_obj.stack if project_obj.stack else "",
                "required_roles": project_obj.required_roles if project_obj.required_roles else ""
            })

        final_recommendations_sorted = sorted(
            processed_candidates,
            key=lambda x: x["final_score"],
            reverse=True
        )[:top_n]

        return [
            {
                "project_id": rec["project_id"],
                "project_name": rec["project_name"],
                "final_score": round(rec["final_score"], 4),
                "base_similarity": round(rec["base_similarity"], 4),
                "bonus_score": round(rec["bonus_score"], 4),
                "required_stack": rec["required_stack"],
                "required_roles": rec["required_roles"],
            } for rec in final_recommendations_sorted
        ]