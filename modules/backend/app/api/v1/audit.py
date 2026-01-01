"""
API Endpoints per Audit Logs
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
import csv
import io
import json

from app.services.database import get_db_session
from app.services.audit_service import get_audit_service, AuditService
from app.models.audit import (
    AuditLogResponse,
    AuditLogFilter,
    AuditLogStats,
    AuditLogSummary,
)

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/", response_model=dict)
async def get_audit_logs(
    # Filtri
    user_id: Optional[str] = Query(None, description="Filtra per user ID"),
    user_email: Optional[str] = Query(None, description="Filtra per email utente"),
    action: Optional[str] = Query(None, description="Filtra per azione"),
    action_category: Optional[str] = Query(None, description="Filtra per categoria"),
    resource_type: Optional[str] = Query(None, description="Filtra per tipo risorsa"),
    resource_id: Optional[str] = Query(None, description="Filtra per ID risorsa"),
    ip_address: Optional[str] = Query(None, description="Filtra per IP"),
    success: Optional[str] = Query(None, description="Filtra per esito (success/failure/error)"),
    date_from: Optional[datetime] = Query(None, description="Data inizio periodo"),
    date_to: Optional[datetime] = Query(None, description="Data fine periodo"),
    # Paginazione
    limit: int = Query(100, ge=1, le=1000, description="Numero risultati"),
    offset: int = Query(0, ge=0, description="Offset paginazione"),
    # Ordinamento
    sort_by: str = Query("timestamp", description="Campo ordinamento"),
    sort_order: str = Query("desc", description="Ordine (asc/desc)"),
    # Sessione DB
    db: AsyncSession = Depends(get_db_session),
):
    """
    Recupera audit logs con filtri avanzati

    Supporta:
    - Filtri per utente, azione, risorsa, periodo
    - Paginazione
    - Ordinamento personalizzato
    """
    try:
        # Crea filtri
        filters = AuditLogFilter(
            user_id=user_id,
            user_email=user_email,
            action=action,
            action_category=action_category,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            success=success,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        # Recupera logs
        audit_service = get_audit_service()
        logs, total = await audit_service.get_logs(db, filters)

        # Converti a response model
        logs_response = [
            AuditLogResponse.model_validate(log) for log in logs
        ]

        return {
            "logs": logs_response,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving audit logs: {str(e)}")


@router.get("/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    log_id: int,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Recupera un singolo audit log per ID
    """
    try:
        audit_service = get_audit_service()
        log = await audit_service.get_log_by_id(db, log_id)

        if not log:
            raise HTTPException(status_code=404, detail="Audit log not found")

        return AuditLogResponse.model_validate(log)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving audit log: {str(e)}")


@router.get("/stats/summary", response_model=AuditLogStats)
async def get_audit_stats(
    date_from: Optional[datetime] = Query(None, description="Data inizio periodo"),
    date_to: Optional[datetime] = Query(None, description="Data fine periodo"),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Recupera statistiche aggregate sui logs

    Ritorna:
    - Totale logs
    - Utenti unici
    - Azioni per tipo
    - Azioni per categoria
    - Success rate
    """
    try:
        audit_service = get_audit_service()
        stats = await audit_service.get_stats(db, date_from, date_to)

        if not stats:
            raise HTTPException(status_code=500, detail="Error calculating statistics")

        return stats

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")


@router.get("/user/{user_id}/activity", response_model=List[AuditLogResponse])
async def get_user_activity(
    user_id: str,
    limit: int = Query(100, ge=1, le=500, description="Numero risultati"),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Recupera l'attività recente di un utente specifico
    """
    try:
        audit_service = get_audit_service()
        logs = await audit_service.get_user_activity(db, user_id, limit)

        return [AuditLogResponse.model_validate(log) for log in logs]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user activity: {str(e)}")


@router.get("/resource/{resource_type}/{resource_id}/history", response_model=List[AuditLogResponse])
async def get_resource_history(
    resource_type: str,
    resource_id: str,
    limit: int = Query(50, ge=1, le=200, description="Numero risultati"),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Recupera lo storico delle azioni su una risorsa specifica
    """
    try:
        audit_service = get_audit_service()
        logs = await audit_service.get_resource_history(db, resource_type, resource_id, limit)

        return [AuditLogResponse.model_validate(log) for log in logs]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving resource history: {str(e)}")


@router.get("/export/json")
async def export_json(
    # Filtri (stessi di GET /)
    user_id: Optional[str] = Query(None),
    user_email: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    action_category: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    ip_address: Optional[str] = Query(None),
    success: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    limit: int = Query(1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Esporta audit logs in formato JSON

    Limiti:
    - Max 10.000 record per export
    - Include tutti i dettagli (request_data, response_data, metadata)
    """
    try:
        # Crea filtri
        filters = AuditLogFilter(
            user_id=user_id,
            user_email=user_email,
            action=action,
            action_category=action_category,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            success=success,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=0,
            sort_by="timestamp",
            sort_order="desc",
        )

        # Export
        audit_service = get_audit_service()
        export_data = await audit_service.export_logs(db, filters, format="json")

        # Aggiungi metadata
        export_response = {
            "export_date": datetime.utcnow().isoformat(),
            "total_records": len(export_data),
            "filters": {
                "user_id": user_id,
                "user_email": user_email,
                "action": action,
                "date_from": date_from.isoformat() if date_from else None,
                "date_to": date_to.isoformat() if date_to else None,
            },
            "logs": export_data,
        }

        return Response(
            content=json.dumps(export_response, indent=2, default=str),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=audit_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting JSON: {str(e)}")


@router.get("/export/csv")
async def export_csv(
    # Filtri (stessi di GET /)
    user_id: Optional[str] = Query(None),
    user_email: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    action_category: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    ip_address: Optional[str] = Query(None),
    success: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    limit: int = Query(1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Esporta audit logs in formato CSV

    Limiti:
    - Max 10.000 record per export
    - Include solo campi base (no request_data, response_data, metadata)
    """
    try:
        # Crea filtri
        filters = AuditLogFilter(
            user_id=user_id,
            user_email=user_email,
            action=action,
            action_category=action_category,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            success=success,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=0,
            sort_by="timestamp",
            sort_order="desc",
        )

        # Export
        audit_service = get_audit_service()
        export_data = await audit_service.export_logs(db, filters, format="csv")

        # Crea CSV
        output = io.StringIO()
        if export_data:
            # Headers
            fieldnames = [
                "id",
                "timestamp",
                "user_email",
                "user_name",
                "action",
                "action_category",
                "resource_type",
                "resource_id",
                "method",
                "endpoint",
                "ip_address",
                "status_code",
                "success",
                "duration_ms",
                "error_message",
            ]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()

            # Rows
            for row in export_data:
                # Filtra solo i campi del CSV
                csv_row = {k: v for k, v in row.items() if k in fieldnames}
                writer.writerow(csv_row)

        csv_content = output.getvalue()

        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=audit_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting CSV: {str(e)}")


@router.post("/cleanup")
async def cleanup_old_logs(
    retention_days: Optional[int] = Query(None, description="Giorni di retention (default: 90)"),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Esegue cleanup manuale dei log più vecchi del periodo di retention

    Richiede permessi admin.
    """
    try:
        audit_service = get_audit_service()
        deleted_count = await audit_service.cleanup_old_logs(db, retention_days)

        return {
            "status": "success",
            "deleted_count": deleted_count,
            "retention_days": retention_days or 90,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up logs: {str(e)}")
