"""
Cache Service - Sistema di cache intelligente multi-layer
"""
import json
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from enum import Enum
import structlog
import redis.asyncio as redis
from cachetools import TTLCache

from ..config.settings import get_settings

logger = structlog.get_logger()

class CacheLevel(Enum):
    """Livelli di cache disponibili"""
    MEMORY = "memory"
    REDIS = "redis"
    PERSISTENT = "persistent"

class DataType(Enum):
    """Tipi di dati per TTL intelligente"""
    REALTIME = "realtime"
    HISTORIC = "historic"
    ALARMS = "alarms"
    TOTALS = "totals"
    DEVICE_INFO = "device_info"
    AGGREGATED = "aggregated"

@dataclass
class CacheKey:
    """Struttura per chiavi di cache strutturate"""
    prefix: str
    data_type: DataType
    device_key: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    
    def __str__(self) -> str:
        """Genera chiave cache standardizzata"""
        key_parts = [self.prefix, self.data_type.value]
        
        if self.device_key:
            key_parts.append(self.device_key)
            
        if self.params:
            # Ordina parametri per chiave consistente
            sorted_params = sorted(self.params.items())
            params_str = "_".join(f"{k}:{v}" for k, v in sorted_params)
            key_parts.append(params_str)
        
        return ":".join(key_parts)

@dataclass 
class CacheEntry:
    """Voce di cache con metadati"""
    data: Any
    timestamp: datetime
    ttl_seconds: int
    data_type: DataType
    hits: int = 0
    
    @property
    def is_expired(self) -> bool:
        """Verifica se la voce è scaduta"""
        age = (datetime.utcnow() - self.timestamp).total_seconds()
        return age > self.ttl_seconds
    
    @property
    def age_seconds(self) -> float:
        """Età della voce in secondi"""
        return (datetime.utcnow() - self.timestamp).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializza per Redis"""
        return {
            "data": json.dumps(self.data, default=str),
            "timestamp": self.timestamp.isoformat(),
            "ttl_seconds": self.ttl_seconds,
            "data_type": self.data_type.value,
            "hits": self.hits
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Deserializza da Redis"""
        return cls(
            data=json.loads(data["data"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            ttl_seconds=data["ttl_seconds"],
            data_type=DataType(data["data_type"]),
            hits=data.get("hits", 0)
        )

class CacheService:
    """Servizio di cache multi-layer intelligente"""
    
    def __init__(self):
        self.settings = get_settings()
        
        # Configurazione TTL per tipo di dato
        self._ttl_config = {
            DataType.REALTIME: 60,          # 1 minuto
            DataType.HISTORIC: 3600,        # 1 ora
            DataType.ALARMS: 30,            # 30 secondi
            DataType.TOTALS: 300,           # 5 minuti
            DataType.DEVICE_INFO: 1800,     # 30 minuti
            DataType.AGGREGATED: 900        # 15 minuti
        }
        
        # Memory cache (L1)
        self.memory_cache = TTLCache(maxsize=1000, ttl=300)
        
        # Redis client (L2) - inizializzato in init()
        self.redis_client: Optional[redis.Redis] = None
        
        # Statistiche
        self.stats = {
            "hits": {"memory": 0, "redis": 0, "total": 0},
            "misses": 0,
            "sets": {"memory": 0, "redis": 0},
            "errors": 0,
            "evictions": 0
        }
        
        # Lock per operazioni atomiche
        self._locks: Dict[str, asyncio.Lock] = {}
    
    async def init(self):
        """Inizializza connessioni cache"""
        try:
            self.redis_client = redis.from_url(
                self.settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30
            )
            
            # Test connessione
            await self.redis_client.ping()
            logger.info("Cache service initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize cache service", error=str(e))
            self.redis_client = None
            raise
    
    async def get(
        self,
        cache_key: Union[str, CacheKey],
        data_type: Optional[DataType] = None
    ) -> Optional[Any]:
        """
        Ottieni dati dalla cache (memory -> redis)
        
        Args:
            cache_key: Chiave cache
            data_type: Tipo dati (per statistics)
            
        Returns:
            Dati dalla cache o None se non trovati
        """
        key_str = str(cache_key)
        
        try:
            # L1: Memory cache
            if key_str in self.memory_cache:
                self.stats["hits"]["memory"] += 1
                self.stats["hits"]["total"] += 1
                
                logger.debug(
                    "Cache hit (memory)",
                    key=key_str,
                    data_type=data_type.value if data_type else "unknown"
                )
                
                return self.memory_cache[key_str]
            
            # L2: Redis cache
            if self.redis_client:
                redis_data = await self.redis_client.hgetall(f"cache:{key_str}")
                
                if redis_data:
                    try:
                        cache_entry = CacheEntry.from_dict(redis_data)
                        
                        # Verifica scadenza
                        if not cache_entry.is_expired:
                            # Aggiorna statistiche
                            cache_entry.hits += 1
                            self.stats["hits"]["redis"] += 1
                            self.stats["hits"]["total"] += 1
                            
                            # Popola memory cache per hit futuri
                            self.memory_cache[key_str] = cache_entry.data
                            
                            # Aggiorna hit count in Redis
                            await self.redis_client.hset(
                                f"cache:{key_str}", 
                                "hits", 
                                cache_entry.hits
                            )
                            
                            logger.debug(
                                "Cache hit (redis)",
                                key=key_str,
                                data_type=cache_entry.data_type.value,
                                age_seconds=cache_entry.age_seconds,
                                hits=cache_entry.hits
                            )
                            
                            return cache_entry.data
                        else:
                            # Rimuovi voce scaduta
                            await self._remove_redis_key(key_str)
                            logger.debug("Removed expired cache entry", key=key_str)
                    
                    except Exception as e:
                        logger.warning("Failed to deserialize cache entry", key=key_str, error=str(e))
                        await self._remove_redis_key(key_str)
            
            # Cache miss
            self.stats["misses"] += 1
            logger.debug("Cache miss", key=key_str)
            return None
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error("Cache get error", key=key_str, error=str(e))
            return None
    
    async def set(
        self,
        cache_key: Union[str, CacheKey],
        data: Any,
        data_type: DataType,
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """
        Salva dati nella cache (memory + redis)
        
        Args:
            cache_key: Chiave cache
            data: Dati da salvare
            data_type: Tipo di dati
            ttl_seconds: TTL custom (opzionale)
            
        Returns:
            True se salvato con successo
        """
        key_str = str(cache_key)
        
        if ttl_seconds is None:
            ttl_seconds = self.get_ttl_for_data_type(data_type)
        
        try:
            # L1: Memory cache
            self.memory_cache[key_str] = data
            self.stats["sets"]["memory"] += 1
            
            # L2: Redis cache
            if self.redis_client:
                cache_entry = CacheEntry(
                    data=data,
                    timestamp=datetime.utcnow(),
                    ttl_seconds=ttl_seconds,
                    data_type=data_type
                )
                
                # Salva in Redis con TTL
                await self.redis_client.hset(
                    f"cache:{key_str}",
                    mapping=cache_entry.to_dict()
                )
                await self.redis_client.expire(f"cache:{key_str}", ttl_seconds)
                
                self.stats["sets"]["redis"] += 1
            
            logger.debug(
                "Cache set",
                key=key_str,
                data_type=data_type.value,
                ttl_seconds=ttl_seconds,
                data_size=len(str(data))
            )
            
            return True
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error("Cache set error", key=key_str, error=str(e))
            return False
    
    async def delete(self, cache_key: Union[str, CacheKey]) -> bool:
        """
        Rimuovi voce dalla cache
        
        Args:
            cache_key: Chiave cache
            
        Returns:
            True se rimosso con successo
        """
        key_str = str(cache_key)
        
        try:
            # Memory cache
            if key_str in self.memory_cache:
                del self.memory_cache[key_str]
            
            # Redis cache
            if self.redis_client:
                await self._remove_redis_key(key_str)
            
            logger.debug("Cache delete", key=key_str)
            return True
            
        except Exception as e:
            logger.error("Cache delete error", key=key_str, error=str(e))
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalida tutte le chiavi che corrispondono al pattern
        
        Args:
            pattern: Pattern di chiavi (es: "device:*")
            
        Returns:
            Numero di chiavi invalidate
        """
        invalidated = 0
        
        try:
            # Memory cache - rimuovi chiavi che matchano
            keys_to_remove = [k for k in self.memory_cache.keys() if self._match_pattern(k, pattern)]
            for key in keys_to_remove:
                del self.memory_cache[key]
                invalidated += 1
            
            # Redis cache
            if self.redis_client:
                redis_pattern = f"cache:{pattern}"
                async for key in self.redis_client.scan_iter(match=redis_pattern):
                    await self.redis_client.delete(key)
                    invalidated += 1
            
            logger.info("Cache invalidation", pattern=pattern, invalidated_count=invalidated)
            return invalidated
            
        except Exception as e:
            logger.error("Cache invalidation error", pattern=pattern, error=str(e))
            return 0
    
    def get_ttl_for_data_type(self, data_type: DataType) -> int:
        """
        Ottieni TTL intelligente basato sul tipo di dato
        
        Args:
            data_type: Tipo di dato
            
        Returns:
            TTL in secondi
        """
        base_ttl = self._ttl_config.get(data_type, 300)
        
        # TTL dinamico basato sull'orario (esempio)
        current_hour = datetime.now().hour
        
        if data_type == DataType.REALTIME:
            # Durante le ore di picco solare, cache più breve
            if 10 <= current_hour <= 16:
                return max(30, base_ttl // 2)
            else:
                return base_ttl * 2
        
        return base_ttl
    
    async def get_cached_data_with_fallback(
        self,
        cache_key: Union[str, CacheKey],
        data_type: DataType,
        fallback_func,
        *args,
        **kwargs
    ) -> Any:
        """
        Ottieni dati dalla cache o esegui fallback function
        
        Args:
            cache_key: Chiave cache
            data_type: Tipo dati
            fallback_func: Funzione da eseguire in caso di cache miss
            *args, **kwargs: Argomenti per fallback_func
            
        Returns:
            Dati dalla cache o dal fallback
        """
        key_str = str(cache_key)
        
        # Ottieni lock per questa chiave per evitare duplicate calls
        if key_str not in self._locks:
            self._locks[key_str] = asyncio.Lock()
        
        async with self._locks[key_str]:
            # Prova prima dalla cache
            cached_data = await self.get(cache_key, data_type)
            if cached_data is not None:
                return cached_data
            
            # Cache miss - esegui fallback
            try:
                logger.debug("Cache miss, executing fallback", key=key_str)
                
                if asyncio.iscoroutinefunction(fallback_func):
                    fresh_data = await fallback_func(*args, **kwargs)
                else:
                    fresh_data = fallback_func(*args, **kwargs)
                
                # Salva in cache
                await self.set(cache_key, fresh_data, data_type)
                
                return fresh_data
                
            except Exception as e:
                logger.error("Fallback function error", key=key_str, error=str(e))
                raise
            finally:
                # Pulisci lock dopo un po'
                asyncio.create_task(self._cleanup_lock(key_str))
    
    async def _cleanup_lock(self, key: str):
        """Pulisci lock dopo 60 secondi per evitare memory leak"""
        await asyncio.sleep(60)
        if key in self._locks:
            del self._locks[key]
    
    async def _remove_redis_key(self, key: str):
        """Helper per rimuovere chiave da Redis"""
        if self.redis_client:
            await self.redis_client.delete(f"cache:{key}")
    
    def _match_pattern(self, key: str, pattern: str) -> bool:
        """Match semplice per pattern con wildcard *"""
        if "*" not in pattern:
            return key == pattern
        
        # Conversione semplice pattern -> regex
        regex_pattern = pattern.replace("*", ".*")
        import re
        return bool(re.match(regex_pattern, key))
    
    def get_stats(self) -> Dict[str, Any]:
        """Ottieni statistiche cache"""
        total_requests = self.stats["hits"]["total"] + self.stats["misses"]
        hit_rate = (self.stats["hits"]["total"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": total_requests,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "sets": self.stats["sets"],
            "errors": self.stats["errors"],
            "memory_cache_size": len(self.memory_cache),
            "memory_cache_maxsize": self.memory_cache.maxsize,
            "redis_connected": self.redis_client is not None,
            "active_locks": len(self._locks)
        }
    
    async def clear_all(self) -> bool:
        """Pulisci tutta la cache"""
        try:
            # Memory cache
            self.memory_cache.clear()
            
            # Redis cache
            if self.redis_client:
                async for key in self.redis_client.scan_iter(match="cache:*"):
                    await self.redis_client.delete(key)
            
            logger.info("Cache cleared completely")
            return True
            
        except Exception as e:
            logger.error("Failed to clear cache", error=str(e))
            return False
    
    async def close(self):
        """Chiudi connessioni cache"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Cache service closed")

# Istanza globale del servizio cache
_cache_service = None

async def get_cache_service() -> CacheService:
    """Ottieni istanza del servizio cache"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
        await _cache_service.init()
    return _cache_service

# Utility functions
def make_cache_key(
    prefix: str,
    data_type: DataType,
    device_key: Optional[str] = None,
    **params
) -> CacheKey:
    """Helper per creare chiavi cache strutturate"""
    return CacheKey(
        prefix=prefix,
        data_type=data_type,
        device_key=device_key,
        params=params if params else None
    )

def make_device_cache_key(device_key: str, data_type: DataType, **params) -> CacheKey:
    """Helper specifico per cache dispositivi"""
    return make_cache_key("device", data_type, device_key, **params) 