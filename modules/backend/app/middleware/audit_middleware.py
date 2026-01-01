"""
Audit Middleware per logging automatico delle richieste API
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import json
from typing import Callable, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware per logging automatico delle richieste API

    Cattura:
    - Informazioni utente da headers/auth
    - Dettagli richiesta (method, endpoint, IP, user-agent)
    - Risposta (status code, durata)
    - Payload richiesta/risposta (sanitizzati)
    """

    def __init__(
        self,
        app: ASGIApp,
        audit_service: Optional[Any] = None,
        exclude_paths: Optional[list] = None,
        log_request_body: bool = True,
        log_response_body: bool = False,
        max_body_length: int = 10000,
    ):
        super().__init__(app)
        self.audit_service = audit_service
        self.exclude_paths = exclude_paths or [
            "/health",
            "/health/liveness",
            "/health/readiness",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
        ]
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.max_body_length = max_body_length

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Processa ogni richiesta e logga l'audit trail"""

        # Skip paths esclusi
        if self._should_skip_path(request.url.path):
            return await call_next(request)

        start_time = time.time()

        # Estrai informazioni dalla richiesta
        audit_data = await self._extract_request_data(request)

        # Variabili per catturare la risposta
        response = None
        error_message = None

        try:
            # Processa la richiesta
            response = await call_next(request)

            # Aggiorna audit data con risposta
            audit_data["status_code"] = response.status_code
            audit_data["success"] = self._determine_success(response.status_code)

        except Exception as e:
            # Cattura errori
            error_message = str(e)
            audit_data["error_message"] = error_message
            audit_data["success"] = "error"
            audit_data["status_code"] = 500
            logger.error(f"Error processing request: {e}", exc_info=True)
            raise

        finally:
            # Calcola durata
            duration_ms = int((time.time() - start_time) * 1000)
            audit_data["duration_ms"] = duration_ms

            # Logga audit in background (non bloccante)
            if self.audit_service:
                try:
                    await self._log_audit(audit_data)
                except Exception as e:
                    # Non fallire la richiesta se il logging fallisce
                    logger.error(f"Failed to log audit: {e}", exc_info=True)

        return response

    def _should_skip_path(self, path: str) -> bool:
        """Verifica se il path deve essere escluso dall'audit"""
        return any(path.startswith(excluded) for excluded in self.exclude_paths)

    async def _extract_request_data(self, request: Request) -> Dict[str, Any]:
        """Estrae dati dalla richiesta per audit log"""

        # Informazioni base
        data = {
            "method": request.method,
            "endpoint": str(request.url.path),
            "ip_address": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "timestamp": datetime.utcnow(),
        }

        # Estrai user info da headers (se presente)
        user_info = self._extract_user_info(request)
        data.update(user_info)

        # Determina azione e categoria
        action_info = self._determine_action(request)
        data.update(action_info)

        # Estrai request body se configurato
        if self.log_request_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await self._get_request_body(request)
                if body:
                    data["request_data"] = self._sanitize_data(body)
            except Exception as e:
                logger.warning(f"Could not extract request body: {e}")

        # Query parameters
        if request.query_params:
            data["extra_metadata"] = data.get("extra_metadata", {})
            data["extra_metadata"]["query_params"] = dict(request.query_params)

        return data

    def _extract_user_info(self, request: Request) -> Dict[str, Any]:
        """Estrae informazioni utente da headers/state"""
        user_info = {}

        # Cerca user info nello state (settato da dependency auth)
        if hasattr(request.state, "user"):
            user = request.state.user
            user_info["user_id"] = getattr(user, "user_id", None)
            user_info["user_email"] = getattr(user, "email", None)
            user_info["user_name"] = getattr(user, "name", None)

        # Fallback: cerca in headers
        if not user_info.get("user_id"):
            # Authorization header
            auth_header = request.headers.get("authorization", "")
            if auth_header:
                user_info["extra_metadata"] = user_info.get("extra_metadata", {})
                user_info["extra_metadata"]["has_auth"] = True

        # Session tracking
        session_id = request.headers.get("x-session-id") or request.cookies.get("session_id")
        if session_id:
            user_info["session_id"] = session_id

        return user_info

    def _determine_action(self, request: Request) -> Dict[str, Any]:
        """Determina il tipo di azione e categoria dalla richiesta"""
        method = request.method
        path = request.url.path

        action_info = {
            "action": "api_access",
            "action_category": "api",
        }

        # Parsing path per determinare azione specifica
        path_parts = [p for p in path.split("/") if p]

        # API versioning
        if len(path_parts) >= 2 and path_parts[0] == "api":
            path_parts = path_parts[2:]  # Skip "api/v1"

        if not path_parts:
            return action_info

        resource = path_parts[0]

        # Device operations
        if resource == "devices":
            action_info["action_category"] = "device"
            action_info["resource_type"] = "device"
            if len(path_parts) > 1:
                action_info["resource_id"] = path_parts[1]
                action_info["action"] = f"device_{method.lower()}"
            else:
                action_info["action"] = "device_list" if method == "GET" else f"device_{method.lower()}"

        # Alarm operations
        elif resource == "alarms":
            action_info["action_category"] = "alarm"
            action_info["resource_type"] = "alarm"
            if len(path_parts) > 1:
                action_info["resource_id"] = path_parts[1]
                if "acknowledge" in path:
                    action_info["action"] = "alarm_acknowledge"
                elif "resolve" in path:
                    action_info["action"] = "alarm_resolve"
                else:
                    action_info["action"] = "alarm_view"
            else:
                action_info["action"] = "alarm_view"

        # Data operations
        elif resource == "data":
            action_info["action_category"] = "data"
            action_info["resource_type"] = "data"
            if "export" in path:
                action_info["action"] = "data_export"
            else:
                action_info["action"] = "data_view"

        # Settings operations
        elif resource == "settings":
            action_info["action_category"] = "settings"
            action_info["resource_type"] = "settings"
            action_info["action"] = "settings_update" if method in ["PUT", "PATCH", "POST"] else "settings_view"

        # Audit operations
        elif resource == "audit":
            action_info["action_category"] = "audit"
            action_info["resource_type"] = "audit"
            action_info["action"] = "audit_view"

        # Auth operations
        elif resource == "auth":
            action_info["action_category"] = "auth"
            if "login" in path:
                action_info["action"] = "login"
            elif "logout" in path:
                action_info["action"] = "logout"
            else:
                action_info["action"] = "auth_access"

        return action_info

    async def _get_request_body(self, request: Request) -> Optional[Dict[str, Any]]:
        """Estrae e parsifica il body della richiesta"""
        try:
            body_bytes = await request.body()
            if not body_bytes:
                return None

            # Limita dimensione
            if len(body_bytes) > self.max_body_length:
                return {"_truncated": True, "_size": len(body_bytes)}

            body_str = body_bytes.decode("utf-8")
            return json.loads(body_str)
        except json.JSONDecodeError:
            return {"_raw": True}
        except Exception as e:
            logger.warning(f"Error parsing request body: {e}")
            return None

    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitizza dati sensibili dal payload"""
        if not isinstance(data, dict):
            return data

        sensitive_keys = [
            "password",
            "token",
            "secret",
            "api_key",
            "apikey",
            "authorization",
            "auth",
            "credential",
            "private_key",
            "privatekey",
        ]

        sanitized = {}
        for key, value in data.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                sanitized[key] = [self._sanitize_data(item) for item in value]
            else:
                sanitized[key] = value

        return sanitized

    def _get_client_ip(self, request: Request) -> str:
        """Estrae IP del client considerando proxy"""
        # X-Forwarded-For header (proxy)
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # X-Real-IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Direct connection
        if request.client:
            return request.client.host

        return "unknown"

    def _determine_success(self, status_code: int) -> str:
        """Determina se la richiesta è andata a buon fine"""
        if 200 <= status_code < 300:
            return "success"
        elif 400 <= status_code < 500:
            return "failure"
        else:
            return "error"

    async def _log_audit(self, audit_data: Dict[str, Any]):
        """Logga l'audit entry usando l'audit service"""
        if self.audit_service:
            try:
                # Importa qui per evitare circular import
                from app.services.database import get_db_session

                # Ottieni sessione DB usando context manager
                async with get_db_session() as db:
                    await self.audit_service.create_log(audit_data, db)
            except Exception as e:
                logger.error(f"Failed to create audit log: {e}", exc_info=True)
