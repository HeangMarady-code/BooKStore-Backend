from fastapi import APIRouter

from app.api.v1.endpoints import admin, auth, books

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(books.router, prefix="/books", tags=["Books"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
