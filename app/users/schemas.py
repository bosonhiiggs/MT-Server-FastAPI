from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=30)
    email: Optional[str] = Field(None, pattern=r"^[^@]+@[^@]+\.[^@]+$")
    password: str = Field(..., min_length=8)

    @model_validator(mode='after')
    def check_username_or_email(self):
        if not self.username and not self.email:
            raise ValueError('Either username or email must be provided')
        return self


class UserResponse(BaseModel):
    class Config:
        # from_attributes=True позволяет создавать Pydantic модель из SQLAlchemy ORM-объекта
        # без явного преобразования (можно передать объект напрямую в return эндпоинта)
        from_attributes = True

    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime