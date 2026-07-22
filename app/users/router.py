from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.db import get_db
from app.core.security import create_access_token
from app.users.dependencies import get_current_user
from app.users.models import UserAccount
from app.users.schemas import UserResponse, UserCreate, UserLogin
from app.users.service import create_user, authenticate_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/signup", response_model=UserResponse)
async def signup(user_create: UserCreate, db: AsyncSession = Depends(get_db)) -> UserResponse:
    return await create_user(user_create=user_create, db=db) # type: ignore


@router.post("/login")
async def login(form_data: UserLogin, db: AsyncSession = Depends(get_db)) -> dict:
    user: UserAccount | None = await authenticate_user(
        username=form_data.username, email=form_data.email, password=form_data.password, db=db
    )
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token: str = create_access_token(data={"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserAccount = Depends(get_current_user)) -> UserResponse:
    return current_user # type: ignore

