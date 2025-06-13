from fastapi import FastAPI
from api.endpoints import recommendations
from db.database import db
from contextlib import asynccontextmanager
from db.project_repository import ProjectRepository
from db.models import Project
from services.recommendation_service import RecommendationService
from services.recommendation_engine import RecommendationEngine
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Connecting to the database...")
    await db.connect()
    print("Database connected.")

    print("Initializing recommendation model...")
    async with db.async_session() as session:
        project_repo = ProjectRepository(session, Project)
        model_service = RecommendationService(model_dir=settings.MODEL_DIR)
        engine = RecommendationEngine(model_service=model_service)
        await engine.initialize(project_repo)
        app.state.recommendation_engine = engine
    print("Recommendation model initialized.")

    yield

    print("Disconnecting from the database...")
    await db.disconnect()
    print("Database disconnected.")

app = FastAPI(lifespan=lifespan)

app.include_router(recommendations.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
