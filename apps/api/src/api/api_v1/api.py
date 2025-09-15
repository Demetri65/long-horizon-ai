from fastapi import APIRouter
from src.api.api_v1.endpoints import llm

api_router = APIRouter()
api_router.include_router(llm.router, prefix="/llm", tags=["llm"])