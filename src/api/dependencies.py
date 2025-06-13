# app/dependencies.py
from services.recommendation_service import RecommendationService
from services.recommendation_engine import RecommendationEngine
import os

def get_recommendation_service():
    model_dir = os.getenv('MODEL_DIR', './models')
    return RecommendationService(model_dir)

def get_recommendation_engine():
    return RecommendationEngine(get_recommendation_service())
