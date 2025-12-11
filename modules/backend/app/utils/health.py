"""
Health Check utilities per SunPulse - Fase 2
"""
import asyncio
from datetime import datetime
from typing import Dict, Any, List
import asyncpg
import redis
import structlog

from ..config.settings import get_settings

logger = structlog.get_logger()

async def check_postgres() -> Dict[str, Any]:
    """Verifica la connessione a PostgreSQL"""
    settings = get_settings()
    start_time = datetime.utcnow()
    
    try:
        conn = await asyncpg.connect(settings.database_url)
        result = await conn.fetchval("SELECT 1")
        await conn.close()
        
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            "healthy": True,
            "service": "postgresql",
            "status": "connected",
            "response_time_ms": round(response_time, 2),
            "database": settings.POSTGRES_DB,
            "host": settings.POSTGRES_HOST
        }
    except Exception as e:
        return {
            "healthy": False,
            "service": "postgresql", 
            "status": "error",
            "error": str(e),
            "database": settings.POSTGRES_DB,
            "host": settings.POSTGRES_HOST
        }

async def check_redis() -> Dict[str, Any]:
    """Verifica la connessione a Redis"""
    settings = get_settings()
    start_time = datetime.utcnow()
    
    try:
        r = redis.from_url(settings.redis_url, decode_responses=True)
        r.ping()
        
        # Ottieni info Redis
        info = r.info()
        r.close()
        
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            "healthy": True,
            "service": "redis",
            "status": "connected",
            "response_time_ms": round(response_time, 2),
            "version": info.get("redis_version", "unknown"),
            "used_memory": info.get("used_memory_human", "unknown"),
            "connected_clients": info.get("connected_clients", 0),
            "host": settings.REDIS_HOST
        }
    except Exception as e:
        return {
            "healthy": False,
            "service": "redis",
            "status": "error", 
            "error": str(e),
            "host": settings.REDIS_HOST
        }

async def check_influxdb() -> Dict[str, Any]:
    """Verifica la connessione a InfluxDB"""
    try:
        # Import dinamico per evitare errori se il servizio non è disponibile
        from ..services.influxdb_writer import get_influxdb_writer
        
        influxdb_writer = await get_influxdb_writer()
        health_data = await influxdb_writer.health_check()
        
        return {
            "service": "influxdb",
            **health_data
        }
    except Exception as e:
        return {
            "healthy": False,
            "service": "influxdb",
            "status": "error",
            "error": str(e)
        }

async def check_cache_service() -> Dict[str, Any]:
    """Verifica il servizio di cache"""
    try:
        from ..services.cache_service import get_cache_service, DataType
        
        cache_service = await get_cache_service()
        stats = cache_service.get_stats()
        
        # Test cache con operazione semplice
        test_key = "health_check_test"
        test_value = {"timestamp": datetime.utcnow().isoformat()}
        
        start_time = datetime.utcnow()
        await cache_service.set(test_key, test_value, DataType.REALTIME, ttl_seconds=10)
        cached_value = await cache_service.get(test_key)
        await cache_service.delete(test_key)
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return {
            "healthy": cached_value is not None,
            "service": "cache",
            "status": "connected" if cached_value else "error",
            "response_time_ms": round(response_time, 2),
            "stats": stats
        }
    except Exception as e:
        return {
            "healthy": False,
            "service": "cache",
            "status": "error",
            "error": str(e)
        }

async def check_zcs_api() -> Dict[str, Any]:
    """Verifica il servizio ZCS API"""
    try:
        from ..services.zcs_api_service import ZCSAPIService
        from ..utils.circuit_breaker import CircuitBreakerRegistry
        
        zcs_service = ZCSAPIService()
        health_data = await zcs_service.health_check()
        
        # Ottieni statistiche circuit breaker
        cb_stats = CircuitBreakerRegistry.get_stats("zcs_api")
        
        return {
            "service": "zcs_api",
            "healthy": health_data.get("healthy", False),
            "status": health_data.get("status", "unknown"),
            "circuit_breaker": cb_stats,
            **health_data
        }
    except Exception as e:
        return {
            "healthy": False,
            "service": "zcs_api",
            "status": "error",
            "error": str(e)
        }

async def check_circuit_breakers() -> Dict[str, Any]:
    """Verifica stato di tutti i circuit breakers"""
    try:
        from ..utils.circuit_breaker import CircuitBreakerRegistry
        
        all_stats = CircuitBreakerRegistry.get_all_stats()
        
        # Determina se ci sono circuit breakers aperti
        any_open = any(
            stats.get("state") == "OPEN" 
            for stats in all_stats.values()
        )
        
        return {
            "healthy": not any_open,
            "service": "circuit_breakers",
            "status": "monitoring",
            "breakers_count": len(all_stats),
            "open_breakers": [
                name for name, stats in all_stats.items()
                if stats.get("state") == "OPEN"
            ],
            "stats": all_stats
        }
    except Exception as e:
        return {
            "healthy": False,
            "service": "circuit_breakers",
            "status": "error",
            "error": str(e)
        }

async def check_celery_workers() -> Dict[str, Any]:
    """Verifica lo stato dei worker Celery"""
    try:
        # TODO: Implementa check worker Celery quando disponibile
        # Per ora ritorniamo stato mock
        return {
            "healthy": True,
            "service": "celery_workers",
            "status": "not_implemented",
            "workers_count": 0,
            "active_tasks": 0
        }
    except Exception as e:
        return {
            "healthy": False,
            "service": "celery_workers",
            "status": "error",
            "error": str(e)
        }

async def get_system_health() -> Dict[str, Any]:
    """Ottieni lo stato di salute di tutto il sistema"""
    start_time = datetime.utcnow()
    
    # Esegui tutti i check in parallelo
    checks = await asyncio.gather(
        check_postgres(),
        check_redis(), 
        check_influxdb(),
        check_cache_service(),
        check_zcs_api(),
        check_circuit_breakers(),
        check_celery_workers(),
        return_exceptions=True
    )
    
    # Filtra le eccezioni
    health_checks = []
    for check in checks:
        if isinstance(check, Exception):
            logger.error("Health check failed", error=str(check))
            health_checks.append({
                "healthy": False,
                "service": "unknown",
                "status": "exception",
                "error": str(check)
            })
        else:
            health_checks.append(check)
    
    # Determina lo stato generale
    all_healthy = all(check.get("healthy", False) for check in health_checks)
    
    # Statistiche di riepilogo
    healthy_services = sum(1 for check in health_checks if check.get("healthy", False))
    total_services = len(health_checks)
    
    check_duration = (datetime.utcnow() - start_time).total_seconds() * 1000
    
    return {
        "healthy": all_healthy,
        "timestamp": datetime.utcnow().isoformat(),
        "check_duration_ms": round(check_duration, 2),
        "summary": {
            "healthy_services": healthy_services,
            "total_services": total_services,
            "health_percentage": round((healthy_services / total_services) * 100, 1)
        },
        "services": health_checks,
        "version": "2.0.0"  # Fase 2 implementata
    } 


class HealthChecker:
    """Classe per gestire controlli di salute del sistema"""
    
    def __init__(self):
        self.logger = structlog.get_logger()
    
    async def check_all(self) -> Dict[str, Any]:
        """Esegui tutti i check di salute"""
        return await get_system_health()
    
    async def check_postgres(self) -> Dict[str, Any]:
        """Check specifico PostgreSQL"""
        return await check_postgres()
    
    async def check_redis(self) -> Dict[str, Any]:
        """Check specifico Redis"""
        return await check_redis()
    
    async def check_influxdb(self) -> Dict[str, Any]:
        """Check specifico InfluxDB"""
        return await check_influxdb()
    
    async def check_cache_service(self) -> Dict[str, Any]:
        """Check specifico servizio cache"""
        return await check_cache_service()
    
    async def check_zcs_api(self) -> Dict[str, Any]:
        """Check specifico ZCS API"""
        return await check_zcs_api()
    
    async def check_circuit_breakers(self) -> Dict[str, Any]:
        """Check specifico circuit breakers"""
        return await check_circuit_breakers()
    
    async def check_celery_workers(self) -> Dict[str, Any]:
        """Check specifico worker Celery"""
        return await check_celery_workers()