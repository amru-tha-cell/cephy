
from fastapi import APIRouter

from app.api.routes import cases, inference

api_router = APIRouter()

api_router.include_router(cases.router)
api_router.include_router(inference.router)
