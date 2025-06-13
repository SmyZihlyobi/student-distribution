from fastapi import FastAPI
from api.endpoints import recommendations
from db.database import db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await db.close()

app = FastAPI(lifespan=lifespan)

app.include_router(recommendations.router)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
