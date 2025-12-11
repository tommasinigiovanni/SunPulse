"""
Endpoint Health per API v1 - Fase 2
"""
from fastapi import APIRouter
from typing import Dict, Any

from ....utils.health import get_system_health
from ....config.settings import get_settings

router = APIRouter()

@router.get("/ping")
async def ping() -> Dict[str, str]:
    """Endpoint di ping semplice"""
    return {"message": "pong", "status": "ok"}

@router.get("/version")
async def version() -> Dict[str, str]:
    """Informazioni sulla versione dell'API"""
    settings = get_settings()
    return {
        "api_version": "2.0.0",  # Fase 2 implementata
        "service": "SunPulse Backend",
        "environment": settings.ENVIRONMENT,
        "phase": "2 - ZCS API Integration & Data Pipeline"
    }

@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Health check completo del sistema"""
    return await get_system_health() 