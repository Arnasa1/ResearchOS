from fastapi import APIRouter, FastAPI, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.database import Base, engine, get_db
from app.models.user import User
from app.schemas.user_schema import UserCreationRequest, UserResponse

import argon2

ph = argon2.PasswordHasher()

router = APIRouter()

app = FastAPI(title="Knowledge OS")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = []

    for error in exc.errors():
        field = ".".join(str(location) for location in error["loc"])

        errors.append({
            "field": field,
            "message": error["msg"],
        })

    return JSONResponse(
        status_code=400,
        content={
            "status": "error",
            "message": "Validation failed",
            "errors": errors,
        },
    )

@app.on_event("startup")
async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    return {"message": "Knowledge OS API"}


@app.post(
    "/users/",
    response_model=UserResponse,
    status_code=201,
)
async def create_user(
    user: UserCreationRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(
            (User.username == user.username) |
            (User.email == user.email)
        )
    )

    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists",
        )

    password_hash = ph.hash(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        password=password_hash,
    )

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

    except Exception:
        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to create user",
        )

    return UserResponse(
        username=new_user.username,
        email=new_user.email,
    )