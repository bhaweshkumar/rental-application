"""Assembles all v1 sub-routers into the top-level api_v1_router.

Phase 1 exports only the /health sub-router. Auth, deals, calculations, and
reports routers will be added in Phases 2 and 3.
"""
from fastapi import APIRouter

from app.auth.router import router as auth_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)

# Phase 3 will add: from app.routers.v1.deals import deals_router, etc.
