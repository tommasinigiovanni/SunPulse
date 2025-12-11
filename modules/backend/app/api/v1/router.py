"""
Router principale API v1 - SunPulse
"""
from fastapi import APIRouter
from .endpoints import health, devices, data, alarms, tasks

api_router = APIRouter()

# Includi i vari router degli endpoint
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(devices.router, prefix="/devices", tags=["Devices"])
api_router.include_router(data.router, prefix="/data", tags=["Data"])
api_router.include_router(alarms.router, prefix="/alarms", tags=["Alarms"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"]) 