"""
Servizio Database per SunPulse
"""
import asyncio
from contextlib import asynccontextmanager
import asyncpg
import redis.asyncio as redis
import structlog
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from ..config.settings import get_settings
from ..models.device import Base
# Import audit models to ensure they're registered with Base
from ..models.audit import AuditLog

logger = structlog.get_logger()

# SQLAlchemy Async Engine
_async_engine = None
_async_session_factory = None

class DatabaseService:
    """Servizio per gestire le connessioni ai database"""
    
    def __init__(self):
        self.settings = get_settings()
        self._postgres_pool = None
        self._redis_client = None
        self._influx_client = None
    
    async def init_postgres(self):
        """Inizializza pool connessioni PostgreSQL"""
        try:
            self._postgres_pool = await asyncpg.create_pool(
                self.settings.database_url,
                min_size=2,
                max_size=20,
                command_timeout=60
            )
            logger.info("PostgreSQL pool inizializzato")
        except Exception as e:
            logger.error("Errore inizializzazione PostgreSQL", error=str(e))
            raise
    
    async def init_redis(self):
        """Inizializza connessione Redis"""
        try:
            self._redis_client = redis.from_url(
                self.settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connessione
            await self._redis_client.ping()
            logger.info("Redis connesso")
        except Exception as e:
            logger.error("Errore connessione Redis", error=str(e))
            raise
    
    async def init_influx(self):
        """Inizializza client InfluxDB"""
        try:
            # Nota: implementazione placeholder per InfluxDB 3.x
            # Sostituire con la configurazione corretta
            logger.info("InfluxDB client inizializzato (placeholder)")
        except Exception as e:
            logger.error("Errore inizializzazione InfluxDB", error=str(e))
            raise
    
    async def close_connections(self):
        """Chiudi tutte le connessioni"""
        if self._postgres_pool:
            await self._postgres_pool.close()
            logger.info("PostgreSQL pool chiuso")
        
        if self._redis_client:
            await self._redis_client.close()
            logger.info("Redis connessione chiusa")
        
        logger.info("Tutte le connessioni database chiuse")
    
    @property
    def postgres_pool(self):
        """Ottieni pool PostgreSQL"""
        return self._postgres_pool
    
    @property
    def redis_client(self):
        """Ottieni client Redis"""
        return self._redis_client
    
    @property
    def influx_client(self):
        """Ottieni client InfluxDB"""
        return self._influx_client

# Istanza globale del servizio database
_db_service = None

async def get_database_service() -> DatabaseService:
    """Ottieni istanza del servizio database"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service

async def init_db():
    """Inizializza tutti i database"""
    logger.info("Inizializzazione database...")
    
    db_service = await get_database_service()
    
    # Inizializza servizi in parallelo per performance migliori
    await asyncio.gather(
        db_service.init_postgres(),
        db_service.init_redis(),
        db_service.init_influx(),
        return_exceptions=True
    )
    
    logger.info("Inizializzazione database completata")

async def close_db():
    """Chiudi connessioni database"""
    global _db_service, _async_engine
    if _db_service:
        await _db_service.close_connections()
        _db_service = None
    if _async_engine:
        await _async_engine.dispose()
        _async_engine = None


async def get_async_engine():
    """Ottieni SQLAlchemy async engine"""
    global _async_engine, _async_session_factory
    
    if _async_engine is None:
        settings = get_settings()
        # Converti URL PostgreSQL per asyncpg
        db_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
        
        _async_engine = create_async_engine(
            db_url,
            poolclass=NullPool,  # Use NullPool per evitare problemi con async
            echo=False,
        )
        
        _async_session_factory = async_sessionmaker(
            bind=_async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        # Crea le tabelle se non esistono
        async with _async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables verified/created")
    
    return _async_engine


@asynccontextmanager
async def get_db_session():
    """Context manager per ottenere una sessione database"""
    global _async_session_factory
    
    if _async_session_factory is None:
        await get_async_engine()
    
    session = _async_session_factory()
    try:
        yield session
    except Exception as e:
        await session.rollback()
        logger.error("Database session error", error=str(e))
        raise
    finally:
        await session.close()