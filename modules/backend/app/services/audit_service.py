"""
Audit Service per gestione audit logs
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, and_, or_, desc, asc
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import logging
from app.models.audit import (
    AuditLog,
    AuditLogCreate,
    AuditLogResponse,
    AuditLogFilter,
    AuditLogStats,
    AuditAction,
)

logger = logging.getLogger(__name__)

class AuditService:
    """
    Service per gestione audit logs con:
    - Creazione automatica log
    - Query con filtri avanzati
    - Retention policy (90 giorni default)
    - Statistiche e aggregazioni
    - Export dati
    """

    def __init__(
        self,
        retention_days: int = 90,
        cleanup_enabled: bool = True,
    ):
        self.retention_days = retention_days
        self.cleanup_enabled = cleanup_enabled

    async def create_log(
        self,
        audit_data: Dict[str, Any],
        db: Optional[AsyncSession] = None,
    ) -> Optional[AuditLog]:
        """
        Crea un nuovo audit log entry

        Args:
            audit_data: Dizionario con i dati dell'audit
            db: Sessione database (opzionale)

        Returns:
            AuditLog creato o None in caso di errore
        """
        try:
            # Crea modello da dict
            audit_log = AuditLog(**audit_data)

            if db:
                db.add(audit_log)
                await db.commit()
                await db.refresh(audit_log)
                logger.debug(f"Audit log created: {audit_log.id}")
                return audit_log
            else:
                # Se non c'è sessione DB, almeno loggiamo
                logger.info(f"Audit log (no DB): {audit_data.get('action')} by {audit_data.get('user_email', 'unknown')}")
                return None

        except Exception as e:
            logger.error(f"Error creating audit log: {e}", exc_info=True)
            if db:
                await db.rollback()
            return None

    async def get_logs(
        self,
        db: AsyncSession,
        filters: Optional[AuditLogFilter] = None,
    ) -> Tuple[List[AuditLog], int]:
        """
        Recupera audit logs con filtri e paginazione

        Args:
            db: Sessione database
            filters: Filtri da applicare

        Returns:
            Tuple di (lista logs, totale)
        """
        try:
            # Base query
            query = select(AuditLog)
            count_query = select(func.count(AuditLog.id))

            # Applica filtri
            conditions = []

            if filters:
                if filters.user_id:
                    conditions.append(AuditLog.user_id == filters.user_id)

                if filters.user_email:
                    conditions.append(AuditLog.user_email.ilike(f"%{filters.user_email}%"))

                if filters.action:
                    conditions.append(AuditLog.action == filters.action)

                if filters.action_category:
                    conditions.append(AuditLog.action_category == filters.action_category)

                if filters.resource_type:
                    conditions.append(AuditLog.resource_type == filters.resource_type)

                if filters.resource_id:
                    conditions.append(AuditLog.resource_id == filters.resource_id)

                if filters.ip_address:
                    conditions.append(AuditLog.ip_address == filters.ip_address)

                if filters.success:
                    conditions.append(AuditLog.success == filters.success)

                if filters.date_from:
                    conditions.append(AuditLog.timestamp >= filters.date_from)

                if filters.date_to:
                    conditions.append(AuditLog.timestamp <= filters.date_to)

            # Applica condizioni
            if conditions:
                query = query.where(and_(*conditions))
                count_query = count_query.where(and_(*conditions))

            # Conteggio totale
            total_result = await db.execute(count_query)
            total = total_result.scalar() or 0

            # Ordinamento
            if filters and filters.sort_by:
                sort_column = getattr(AuditLog, filters.sort_by, AuditLog.timestamp)
                if filters.sort_order == "asc":
                    query = query.order_by(asc(sort_column))
                else:
                    query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(desc(AuditLog.timestamp))

            # Paginazione
            if filters:
                query = query.offset(filters.offset).limit(filters.limit)

            # Esegui query
            result = await db.execute(query)
            logs = result.scalars().all()

            return list(logs), total

        except Exception as e:
            logger.error(f"Error getting audit logs: {e}", exc_info=True)
            return [], 0

    async def get_log_by_id(
        self,
        db: AsyncSession,
        log_id: int,
    ) -> Optional[AuditLog]:
        """
        Recupera un singolo audit log per ID

        Args:
            db: Sessione database
            log_id: ID del log

        Returns:
            AuditLog o None se non trovato
        """
        try:
            query = select(AuditLog).where(AuditLog.id == log_id)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting audit log {log_id}: {e}", exc_info=True)
            return None

    async def get_stats(
        self,
        db: AsyncSession,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Optional[AuditLogStats]:
        """
        Recupera statistiche aggregate sui logs

        Args:
            db: Sessione database
            date_from: Data inizio periodo
            date_to: Data fine periodo

        Returns:
            AuditLogStats o None
        """
        try:
            # Periodo default: ultimi 30 giorni
            if not date_from:
                date_from = datetime.utcnow() - timedelta(days=30)
            if not date_to:
                date_to = datetime.utcnow()

            # Query base con filtro periodo
            base_query = select(AuditLog).where(
                and_(
                    AuditLog.timestamp >= date_from,
                    AuditLog.timestamp <= date_to,
                )
            )

            # Totale logs
            total_query = select(func.count(AuditLog.id)).where(
                and_(
                    AuditLog.timestamp >= date_from,
                    AuditLog.timestamp <= date_to,
                )
            )
            total_result = await db.execute(total_query)
            total_logs = total_result.scalar() or 0

            # Utenti unici
            unique_users_query = select(func.count(func.distinct(AuditLog.user_id))).where(
                and_(
                    AuditLog.timestamp >= date_from,
                    AuditLog.timestamp <= date_to,
                    AuditLog.user_id.isnot(None),
                )
            )
            unique_users_result = await db.execute(unique_users_query)
            unique_users = unique_users_result.scalar() or 0

            # Azioni per tipo
            actions_query = select(
                AuditLog.action,
                func.count(AuditLog.id).label("count")
            ).where(
                and_(
                    AuditLog.timestamp >= date_from,
                    AuditLog.timestamp <= date_to,
                )
            ).group_by(AuditLog.action)
            actions_result = await db.execute(actions_query)
            actions_by_type = {row[0]: row[1] for row in actions_result.fetchall()}

            # Azioni per categoria
            categories_query = select(
                AuditLog.action_category,
                func.count(AuditLog.id).label("count")
            ).where(
                and_(
                    AuditLog.timestamp >= date_from,
                    AuditLog.timestamp <= date_to,
                    AuditLog.action_category.isnot(None),
                )
            ).group_by(AuditLog.action_category)
            categories_result = await db.execute(categories_query)
            actions_by_category = {row[0]: row[1] for row in categories_result.fetchall()}

            # Success rate
            success_query = select(func.count(AuditLog.id)).where(
                and_(
                    AuditLog.timestamp >= date_from,
                    AuditLog.timestamp <= date_to,
                    AuditLog.success == "success",
                )
            )
            success_result = await db.execute(success_query)
            success_count = success_result.scalar() or 0
            success_rate = (success_count / total_logs * 100) if total_logs > 0 else 0

            return AuditLogStats(
                total_logs=total_logs,
                unique_users=unique_users,
                actions_by_type=actions_by_type,
                actions_by_category=actions_by_category,
                success_rate=round(success_rate, 2),
                period_start=date_from,
                period_end=date_to,
            )

        except Exception as e:
            logger.error(f"Error getting audit stats: {e}", exc_info=True)
            return None

    async def cleanup_old_logs(
        self,
        db: AsyncSession,
        retention_days: Optional[int] = None,
    ) -> int:
        """
        Rimuove log più vecchi del periodo di retention

        Args:
            db: Sessione database
            retention_days: Giorni di retention (default: self.retention_days)

        Returns:
            Numero di log eliminati
        """
        if not self.cleanup_enabled:
            logger.info("Cleanup disabled")
            return 0

        try:
            retention = retention_days or self.retention_days
            cutoff_date = datetime.utcnow() - timedelta(days=retention)

            # Query per eliminazione
            delete_query = delete(AuditLog).where(
                AuditLog.timestamp < cutoff_date
            )

            result = await db.execute(delete_query)
            await db.commit()

            deleted_count = result.rowcount
            logger.info(f"Cleaned up {deleted_count} audit logs older than {retention} days")

            return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning up audit logs: {e}", exc_info=True)
            await db.rollback()
            return 0

    async def export_logs(
        self,
        db: AsyncSession,
        filters: Optional[AuditLogFilter] = None,
        format: str = "json",
    ) -> List[Dict[str, Any]]:
        """
        Esporta logs in formato JSON o CSV-compatible

        Args:
            db: Sessione database
            filters: Filtri da applicare
            format: Formato export ("json" o "csv")

        Returns:
            Lista di dizionari con i dati
        """
        try:
            logs, _ = await self.get_logs(db, filters)

            export_data = []
            for log in logs:
                data = {
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                    "user_email": log.user_email,
                    "user_name": log.user_name,
                    "action": log.action,
                    "action_category": log.action_category,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "method": log.method,
                    "endpoint": log.endpoint,
                    "ip_address": log.ip_address,
                    "status_code": log.status_code,
                    "success": log.success,
                    "duration_ms": log.duration_ms,
                    "error_message": log.error_message,
                }

                if format == "json":
                    # Include dati completi per JSON
                    data["user_agent"] = log.user_agent
                    data["request_data"] = log.request_data
                    data["response_data"] = log.response_data
                    data["metadata"] = log.metadata

                export_data.append(data)

            return export_data

        except Exception as e:
            logger.error(f"Error exporting audit logs: {e}", exc_info=True)
            return []

    async def get_user_activity(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 100,
    ) -> List[AuditLog]:
        """
        Recupera l'attività recente di un utente

        Args:
            db: Sessione database
            user_id: ID utente
            limit: Numero massimo di risultati

        Returns:
            Lista di AuditLog
        """
        try:
            query = (
                select(AuditLog)
                .where(AuditLog.user_id == user_id)
                .order_by(desc(AuditLog.timestamp))
                .limit(limit)
            )

            result = await db.execute(query)
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"Error getting user activity: {e}", exc_info=True)
            return []

    async def get_resource_history(
        self,
        db: AsyncSession,
        resource_type: str,
        resource_id: str,
        limit: int = 50,
    ) -> List[AuditLog]:
        """
        Recupera lo storico di una risorsa specifica

        Args:
            db: Sessione database
            resource_type: Tipo di risorsa
            resource_id: ID risorsa
            limit: Numero massimo di risultati

        Returns:
            Lista di AuditLog
        """
        try:
            query = (
                select(AuditLog)
                .where(
                    and_(
                        AuditLog.resource_type == resource_type,
                        AuditLog.resource_id == resource_id,
                    )
                )
                .order_by(desc(AuditLog.timestamp))
                .limit(limit)
            )

            result = await db.execute(query)
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"Error getting resource history: {e}", exc_info=True)
            return []


# Singleton instance
_audit_service_instance: Optional[AuditService] = None


def get_audit_service(
    retention_days: int = 90,
    cleanup_enabled: bool = True,
) -> AuditService:
    """
    Ottiene o crea l'istanza singleton del service

    Args:
        retention_days: Giorni di retention
        cleanup_enabled: Abilita cleanup automatico

    Returns:
        AuditService instance
    """
    global _audit_service_instance
    if _audit_service_instance is None:
        _audit_service_instance = AuditService(
            retention_days=retention_days,
            cleanup_enabled=cleanup_enabled,
        )
    return _audit_service_instance
