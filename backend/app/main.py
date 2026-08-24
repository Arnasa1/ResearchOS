from fastapi import APIRouter, FastAPI

from app.database import Base, engine
from app.models.user import User

router = APIRouter()

app = FastAPI(title="Knowledge OS")

@app.on_event("startup")
async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Knowledge OS API"}