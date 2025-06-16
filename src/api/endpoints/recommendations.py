from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from services.recommendation_engine import RecommendationEngine
from db import get_repositories, Repositories
from api.dependencies import get_recommendation_engine

recommendation_router = APIRouter(prefix="/recommendations", tags=["recommendations"])

class RecommendationResponse(BaseModel):
    project_id: int
    project_name: str
    final_score: float
    base_similarity: float
    bonus_score: float
    required_stack: str
    required_roles: str

recommendations_cache: Dict[tuple, List[Dict[str, Any]]] = {}

@recommendation_router.get("/student/{student_id}", response_model=List[RecommendationResponse])
async def get_student_recommendations(
    student_id: int,
    top_n: int = 5,
    repos: Repositories = Depends(get_repositories),
    engine: RecommendationEngine = Depends(get_recommendation_engine)
):
    cache_key = (student_id, top_n)

    if cache_key in recommendations_cache:
        print(f"Cache hit for student_id={student_id}, top_n={top_n}")
        recommendations = recommendations_cache[cache_key]
    else:
        print(f"Cache miss for student_id={student_id}, top_n={top_n}. Fetching from engine...")
        try:
            student_repo = repos.student_repo
            project_repo = repos.project_repo

            recommendations = await engine.get_recommendations(
                student_id=student_id,
                student_repo=student_repo,
                project_repo=project_repo,
                top_n=top_n
            )

            recommendations_cache[cache_key] = recommendations

        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return [
        RecommendationResponse(
            project_id=rec["project_id"],
            project_name=rec["project_name"],
            final_score=rec["final_score"],
            base_similarity=rec["base_similarity"],
            bonus_score=rec["bonus_score"],
            required_stack=rec["required_stack"],
            required_roles=rec["required_roles"]
        )
        for rec in recommendations
    ]