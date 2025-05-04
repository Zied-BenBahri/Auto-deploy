from fastapi import FastAPI
from app.routes import router as app_router

app = FastAPI(
    title="My FastAPI Project",
    description="API for my project",
    version="0.1.0"
)
app.include_router(app_router)

