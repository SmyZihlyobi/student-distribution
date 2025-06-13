from services.recommendation_model import RecommendationService
from services.recommendation_engine import RecommendationEngine
import os

def get_recommendation_service():
    return RecommendationService()

def get_recommendation_engine():
    return RecommendationEngine(get_recommendation_service())
