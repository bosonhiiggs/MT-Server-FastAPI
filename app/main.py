from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.users.router import router as users_router

app = FastAPI(
    title="MT server FastAPI",
    description="Music education platform API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware, # type: ignore
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)

@app.get("/")
async def root():
    return {"message": "MT-Server-FastAPI"}