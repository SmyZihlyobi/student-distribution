from fastapi import FastAPI
from api.endpoints import recommendations
from db.database import db
from contextlib import asynccontextmanager
from services.recommendation_service import RecommendationService
from services.recommendation_engine import RecommendationEngine
from config import settings
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Connecting to the database...")
    await db.connect()
    print("Database connected.")

    print("Initializing recommendation model...")
    model_dir_path = Path(__file__).parent / settings.MODEL_DIR
    model_service = RecommendationService(model_dir=str(model_dir_path))
    engine = RecommendationEngine(model_service=model_service)
    app.state.recommendation_engine = engine
    print("Recommendation model initialized.")

    yield

    print("Disconnecting from the database...")
    await db.disconnect()
    print("Database disconnected.")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommendations.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
