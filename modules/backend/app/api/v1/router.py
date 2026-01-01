"""
Router principale API v1 - SunPulse
"""
from fastapi import APIRouter
from .endpoints import health, devices, data, alarms, tasks, notifications, device_management, websocket

api_router = APIRouter()

# Includi i vari router degli endpoint
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(devices.router, prefix="/devices", tags=["Devices"])
api_router.include_router(device_management.router, prefix="/device-management", tags=["Device Management"])
api_router.include_router(data.router, prefix="/data", tags=["Data"])
api_router.include_router(alarms.router, prefix="/alarms", tags=["Alarms"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(websocket.router, tags=["WebSocket"]) 