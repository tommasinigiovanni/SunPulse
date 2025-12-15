"""
Notifications endpoints - Gestione notifiche email
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
import structlog

from ....services.email_service import get_email_service

logger = structlog.get_logger()

router = APIRouter()


class TestEmailRequest(BaseModel):
    """Request per invio email di test"""
    email: EmailStr


class AlarmNotificationRequest(BaseModel):
    """Request per notifica allarme"""
    alarm_type: str
    alarm_message: str
    device_name: str
    severity: str = "warning"


@router.get("/status")
async def get_notification_status() -> Dict[str, Any]:
    """Ottieni stato del servizio notifiche"""
    email_service = get_email_service()
    
    return {
        "email_configured": email_service.is_configured,
        "notification_email": email_service.notification_email,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/test")
async def send_test_email(request: TestEmailRequest) -> Dict[str, Any]:
    """Invia email di test"""
    email_service = get_email_service()
    
    if not email_service.is_configured:
        raise HTTPException(
            status_code=503,
            detail="Email service not configured. Set RESEND_API_KEY in environment."
        )
    
    result = await email_service.send_test_email(request.email)
    
    if result.get("success"):
        logger.info("Test email sent", to=request.email)
        return {
            "message": f"Email di test inviata a {request.email}",
            "success": True,
            "email_id": result.get("id")
        }
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {result.get('error')}"
        )


@router.post("/alarm")
async def send_alarm_notification(request: AlarmNotificationRequest) -> Dict[str, Any]:
    """Invia notifica per allarme"""
    email_service = get_email_service()
    
    if not email_service.is_configured:
        raise HTTPException(
            status_code=503,
            detail="Email service not configured"
        )
    
    result = await email_service.send_alarm_notification(
        alarm_type=request.alarm_type,
        alarm_message=request.alarm_message,
        device_name=request.device_name,
        severity=request.severity
    )
    
    if result.get("success"):
        return {
            "message": "Notifica allarme inviata",
            "success": True,
            "email_id": result.get("id")
        }
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send notification: {result.get('error')}"
        )


@router.post("/daily-report")
async def send_daily_report() -> Dict[str, Any]:
    """Invia report giornaliero con i dati attuali"""
    from ..endpoints.data import get_realtime_data
    
    email_service = get_email_service()
    
    if not email_service.is_configured:
        raise HTTPException(
            status_code=503,
            detail="Email service not configured"
        )
    
    # Ottieni dati correnti
    try:
        realtime = await get_realtime_data()
        summary = realtime.get("summary", {})
        
        production = summary.get("total_energy_today", 0)
        consumption = summary.get("energy_consumed_today", 0)
        self_consumption = summary.get("energy_self_consumed_today", 0)
        from_grid = summary.get("energy_from_grid_today", 0)
        to_grid = summary.get("energy_to_grid_today", 0)
        
        # Calcola risparmio (€0.25/kWh autoconsumo + €0.10/kWh venduto)
        savings = (self_consumption * 0.25) + (to_grid * 0.10)
        
        result = await email_service.send_daily_report(
            production_kwh=production,
            consumption_kwh=consumption,
            self_consumption_kwh=self_consumption,
            from_grid_kwh=from_grid,
            to_grid_kwh=to_grid,
            savings_eur=savings
        )
        
        if result.get("success"):
            return {
                "message": "Report giornaliero inviato",
                "success": True,
                "email_id": result.get("id"),
                "data": {
                    "production_kwh": production,
                    "consumption_kwh": consumption,
                    "savings_eur": savings
                }
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send report: {result.get('error')}"
            )
            
    except Exception as e:
        logger.error("Failed to send daily report", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )
