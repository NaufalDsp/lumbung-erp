from fastapi import APIRouter

from app.api.v1.audit import router as audit_router
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.master import router as master_router
from app.api.v1.purchasing import router as purchasing_router
from app.api.v1.stock import router as stock_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(auth_router)
api_router.include_router(master_router)
api_router.include_router(purchasing_router)
api_router.include_router(stock_router)
api_router.include_router(audit_router)
