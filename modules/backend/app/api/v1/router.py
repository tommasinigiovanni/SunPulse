"""
Router principale API v1 - SunPulse

JWT Authentication enabled for protected endpoints.
Auth0 API Audience: AUTH0_API_AUDIENCE env variable (default: https://sunpulse-api)
"""
from fastapi import APIRouter, Depends
from .endpoints import health, devices, data, alarms, tasks, notifications, device_management, websocket, settings
from . import audit
from ...auth import get_current_user, require_auth

api_router = APIRouter()

# ============================================
# PUBLIC ENDPOINTS (no authentication required)
# ============================================
api_router.include_router(health.router, prefix="/health", tags=["Health"])

# ============================================
# PROTECTED ENDPOINTS (authentication required)
# ============================================
auth_dependency = [Depends(get_current_user)]

api_router.include_router(
    devices.router, 
    prefix="/devices", 
    tags=["Devices"],
    dependencies=auth_dependency
)
api_router.include_router(
    device_management.router, 
    prefix="/device-management", 
    tags=["Device Management"],
    dependencies=auth_dependency
)
api_router.include_router(
    data.router, 
    prefix="/data", 
    tags=["Data"],
    dependencies=auth_dependency
)
api_router.include_router(
    alarms.router, 
    prefix="/alarms", 
    tags=["Alarms"],
    dependencies=auth_dependency
)
api_router.include_router(
    notifications.router, 
    prefix="/notifications", 
    tags=["Notifications"],
    dependencies=auth_dependency
)
api_router.include_router(
    settings.router, 
    prefix="/settings", 
    tags=["Settings"],
    dependencies=auth_dependency
)
api_router.include_router(
    websocket.router, 
    tags=["WebSocket"]
    # WebSocket gestisce auth separatamente
)

# ============================================
# ADMIN ENDPOINTS (admin role required)
# ============================================
admin_dependency = [Depends(require_auth(roles=["admin"]))]

api_router.include_router(
    tasks.router, 
    prefix="/tasks", 
    tags=["Tasks"],
    dependencies=admin_dependency
)
api_router.include_router(
    audit.router, 
    tags=["Audit"],
    dependencies=admin_dependency
)
