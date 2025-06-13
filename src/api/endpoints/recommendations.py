from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from services.recommendation_engine import RecommendationEngine
from db import get_repositories


router = APIRouter(prefix="/recommendations", tags=["recommendations"])

class RecommendationResponse(BaseModel):
    project_id: int
    project_name: str
    match_score: float
    required_stack: str
    required_roles: str


@router.get("/student/{student_id}", response_model=List[RecommendationResponse])
async def get_student_recommendations(
    student_id: int,
    top_n: int = 5,
    repos: dict = Depends(get_repositories),
    engine: RecommendationEngine = Depends()
):
    try:
        # Получаем репозитории
        student_repo = repos['student_repo']
        project_repo = repos['project_repo']
        
        # Получаем рекомендации
        recommendations = await engine.get_recommendations(
            student_id=student_id,
            student_repo=student_repo,
            project_repo=project_repo,
            top_n=top_n
        )
        
        # Преобразуем в Pydantic модель
        return [
            RecommendationResponse(
                project_id=rec["project_id"],
                project_name=rec["project_name"],
                match_score=rec["match_score"],
                required_stack=rec["required_stack"],
                required_roles=rec["required_roles"]
            )
            for rec in recommendations
        ]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))