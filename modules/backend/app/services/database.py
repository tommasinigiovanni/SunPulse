"""
Servizio Database per SunPulse
"""
import asyncio
import asyncpg
import redis.asyncio as redis
import structlog

from ..config.settings import get_settings

logger = structlog.get_logger()

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
    global _db_service
    if _db_service:
        await _db_service.close_connections()
        _db_service = None 