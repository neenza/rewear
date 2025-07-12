from fastapi import APIRouter

from app.api.endpoints import auth, users, items, swaps, admin

# Main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(items.router, prefix="/items", tags=["Items"])
api_router.include_router(swaps.router, prefix="/swaps", tags=["Swaps"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
