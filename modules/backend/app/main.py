"""
SunPulse Backend API
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog
import uvicorn

from .config.settings import get_settings
from .api.v1.router import api_router
from .services.database import init_db
from .utils.health import HealthChecker

# Configurazione logging
logger = structlog.get_logger()

def create_app() -> FastAPI:
    """Crea e configura l'applicazione FastAPI"""
    settings = get_settings()
    
    app = FastAPI(
        title="SunPulse API",
        description="API per il monitoraggio di impianti fotovoltaici",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
    )
    
    # Middleware CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Middleware per host fidati
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"],
    )
    
    # Router API
    app.include_router(api_router, prefix="/api/v1")
    
    return app

# Crea l'istanza dell'app
app = create_app()

@app.on_event("startup")
async def startup_event():
    """Inizializzazione all'avvio dell'applicazione"""
    logger.info("Avvio SunPulse Backend...")
    
    # Inizializza database
    await init_db()
    logger.info("Database inizializzato")

@app.on_event("shutdown")
async def shutdown_event():
    """Operazioni di chiusura"""
    logger.info("Chiusura SunPulse Backend...")

@app.get("/")
async def root():
    """Endpoint root"""
    return {
        "message": "SunPulse API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint per Docker e monitoring"""
    health_checker = HealthChecker()
    health_status = await health_checker.check_all()
    
    status_code = 200 if health_status.get("healthy", False) else 503
    
    return JSONResponse(
        status_code=status_code,
        content=health_status
    )

@app.get("/health/liveness")
async def liveness_probe():
    """Liveness probe per Kubernetes"""
    return {"status": "alive", "timestamp": "2024-01-01T00:00:00Z"}

@app.get("/health/readiness")
async def readiness_probe():
    """Readiness probe per Kubernetes"""
    health_checker = HealthChecker()
    
    # Controlla solo i servizi critici per la readiness
    db_status = await health_checker.check_postgres()
    redis_status = await health_checker.check_redis()
    
    if db_status["status"] == "healthy" and redis_status["status"] == "healthy":
        return {"status": "ready", "timestamp": "2024-01-01T00:00:00Z"}
    else:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "timestamp": "2024-01-01T00:00:00Z"}
        )

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    ) 