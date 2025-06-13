from services.recommendation_engine import RecommendationEngine
from fastapi import Request

def get_recommendation_engine(request: Request) -> RecommendationEngine:
    """Обёртка для получения RecommendationEngine из FastAPI"""
    return request.app.state.recommendation_engine

