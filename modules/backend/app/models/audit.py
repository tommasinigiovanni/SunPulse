"""
Audit Log Models
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum as PyEnum
from pydantic import BaseModel, Field

# Importa Base dal modulo device per consistenza
from app.models.device import Base

class AuditAction(PyEnum):
    """Tipi di azioni audit"""
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"

    # Device operations
    DEVICE_CREATE = "device_create"
    DEVICE_UPDATE = "device_update"
    DEVICE_DELETE = "device_delete"
    DEVICE_VIEW = "device_view"

    # Configuration
    CONFIG_UPDATE = "config_update"
    CONFIG_VIEW = "config_view"

    # Alarms
    ALARM_ACKNOWLEDGE = "alarm_acknowledge"
    ALARM_RESOLVE = "alarm_resolve"
    ALARM_VIEW = "alarm_view"

    # Data access
    DATA_EXPORT = "data_export"
    DATA_VIEW = "data_view"
    REPORT_GENERATE = "report_generate"

    # Settings
    SETTINGS_UPDATE = "settings_update"
    SETTINGS_VIEW = "settings_view"

    # User management
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    USER_VIEW = "user_view"

    # API access
    API_ACCESS = "api_access"
    API_ERROR = "api_error"

    # System
    SYSTEM_ERROR = "system_error"
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"

class AuditLog(Base):
    """Modello per il log delle azioni di audit"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # User information
    user_id = Column(String(255), nullable=True, index=True)  # Auth0 user ID o "system"
    user_email = Column(String(255), nullable=True, index=True)
    user_name = Column(String(255), nullable=True)

    # Action details
    action = Column(String(50), nullable=False, index=True)  # Tipo di azione
    action_category = Column(String(50), nullable=True, index=True)  # Categoria (auth, device, data, etc.)
    resource_type = Column(String(50), nullable=True, index=True)  # Tipo di risorsa (device, alarm, user, etc.)
    resource_id = Column(String(255), nullable=True, index=True)  # ID della risorsa

    # Request details
    method = Column(String(10), nullable=True)  # HTTP method (GET, POST, PUT, DELETE, etc.)
    endpoint = Column(String(500), nullable=True)  # API endpoint
    ip_address = Column(String(45), nullable=True, index=True)  # IPv4 o IPv6
    user_agent = Column(Text, nullable=True)  # Browser/client info

    # Response details
    status_code = Column(Integer, nullable=True, index=True)  # HTTP status code
    success = Column(String(10), nullable=True, index=True)  # "success", "failure", "error"
    error_message = Column(Text, nullable=True)  # Messaggio di errore se presente

    # Additional context
    request_data = Column(JSON, nullable=True)  # Dati della richiesta (body, query params)
    response_data = Column(JSON, nullable=True)  # Dati della risposta (limitati)
    metadata = Column(JSON, nullable=True)  # Metadati aggiuntivi

    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    duration_ms = Column(Integer, nullable=True)  # Durata in millisecondi

    # Session tracking
    session_id = Column(String(255), nullable=True, index=True)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, user={self.user_email}, action={self.action}, timestamp={self.timestamp})>"

# Indici compositi per query comuni
Index('idx_audit_user_timestamp', AuditLog.user_id, AuditLog.timestamp)
Index('idx_audit_action_timestamp', AuditLog.action, AuditLog.timestamp)
Index('idx_audit_resource', AuditLog.resource_type, AuditLog.resource_id)
Index('idx_audit_timestamp_action', AuditLog.timestamp, AuditLog.action)

# ==============================================================================
# Pydantic Models (API & Validation)
# ==============================================================================

class AuditLogCreate(BaseModel):
    """Schema per creazione audit log"""
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    action: str
    action_category: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    method: Optional[str] = None
    endpoint: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status_code: Optional[int] = None
    success: Optional[str] = None
    error_message: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None
    session_id: Optional[str] = None

class AuditLogResponse(BaseModel):
    """Schema risposta audit log"""
    id: int
    user_id: Optional[str]
    user_email: Optional[str]
    user_name: Optional[str]
    action: str
    action_category: Optional[str]
    resource_type: Optional[str]
    resource_id: Optional[str]
    method: Optional[str]
    endpoint: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    status_code: Optional[int]
    success: Optional[str]
    error_message: Optional[str]
    request_data: Optional[Dict[str, Any]]
    response_data: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    timestamp: datetime
    duration_ms: Optional[int]
    session_id: Optional[str]

    class Config:
        from_attributes = True

class AuditLogFilter(BaseModel):
    """Schema per filtri audit log"""
    user_id: Optional[str] = Field(None, description="Filtra per user ID")
    user_email: Optional[str] = Field(None, description="Filtra per email utente")
    action: Optional[str] = Field(None, description="Filtra per tipo azione")
    action_category: Optional[str] = Field(None, description="Filtra per categoria")
    resource_type: Optional[str] = Field(None, description="Filtra per tipo risorsa")
    resource_id: Optional[str] = Field(None, description="Filtra per ID risorsa")
    ip_address: Optional[str] = Field(None, description="Filtra per IP address")
    success: Optional[str] = Field(None, description="Filtra per esito (success/failure/error)")
    date_from: Optional[datetime] = Field(None, description="Data inizio periodo")
    date_to: Optional[datetime] = Field(None, description="Data fine periodo")
    limit: int = Field(100, ge=1, le=1000, description="Numero massimo risultati")
    offset: int = Field(0, ge=0, description="Offset per paginazione")
    sort_by: str = Field("timestamp", description="Campo per ordinamento")
    sort_order: str = Field("desc", description="Ordine (asc/desc)")

class AuditLogStats(BaseModel):
    """Statistiche audit log"""
    total_logs: int
    unique_users: int
    actions_by_type: Dict[str, int]
    actions_by_category: Dict[str, int]
    success_rate: float
    period_start: datetime
    period_end: datetime

class AuditLogSummary(BaseModel):
    """Riepilogo audit log per export"""
    logs: List[AuditLogResponse]
    total: int
    stats: Optional[AuditLogStats] = None
