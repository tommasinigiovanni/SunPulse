"""
Circuit Breaker Pattern - Protezione contro fallimenti a cascata
"""
import asyncio
import time
from enum import Enum
from typing import Callable, Any, Optional
import structlog

logger = structlog.get_logger()

class CircuitState(Enum):
    """Stati del Circuit Breaker"""
    CLOSED = "closed"       # Normale funzionamento
    OPEN = "open"           # Circuito aperto, richieste bloccate
    HALF_OPEN = "half_open" # Test per verifica recupero

class CircuitBreakerError(Exception):
    """Eccezione sollevata quando il circuit breaker è aperto"""
    pass

class CircuitBreaker:
    """
    Circuit Breaker per proteggere servizi esterni da fallimenti
    
    Stati:
    - CLOSED: Normale funzionamento, tutte le richieste passano
    - OPEN: Circuito aperto, richieste bloccate per recovery_timeout
    - HALF_OPEN: Test di una richiesta per verificare il recupero
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 2,
        service_name: str = "unknown"
    ):
        self.failure_threshold = failure_threshold      # Numero fallimenti per aprire
        self.recovery_timeout = recovery_timeout        # Secondi prima di tentare recupero
        self.success_threshold = success_threshold      # Successi per chiudere il circuito
        self.service_name = service_name
        
        # Stato interno
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.next_attempt_time: Optional[float] = None
        
        # Statistiche
        self.total_requests = 0
        self.total_failures = 0
        self.total_successes = 0
        self.state_changes = 0
        
        # Lock per thread safety
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Esegue una funzione attraverso il circuit breaker
        
        Args:
            func: Funzione da eseguire
            *args, **kwargs: Argomenti per la funzione
            
        Returns:
            Risultato della funzione
            
        Raises:
            CircuitBreakerError: Se il circuito è aperto
        """
        async with self._lock:
            self.total_requests += 1
            
            # Verifica stato del circuito
            await self._check_state()
            
            if self.state == CircuitState.OPEN:
                logger.warning(
                    "Circuit breaker open, blocking request",
                    service=self.service_name,
                    failure_count=self.failure_count,
                    seconds_until_retry=self._seconds_until_retry()
                )
                raise CircuitBreakerError(
                    f"Circuit breaker open for {self.service_name}. "
                    f"Retry in {self._seconds_until_retry()} seconds"
                )
        
        # Esegui la funzione
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
            
        except Exception as e:
            await self._on_failure(e)
            raise
    
    async def _check_state(self):
        """Verifica e aggiorna lo stato del circuit breaker"""
        current_time = time.time()
        
        if self.state == CircuitState.OPEN:
            # Verifica se è tempo di tentare un recupero
            if self.next_attempt_time and current_time >= self.next_attempt_time:
                await self._transition_to_half_open()
        
        elif self.state == CircuitState.HALF_OPEN:
            # In half-open, permettiamo una richiesta di test
            pass
    
    async def _on_success(self):
        """Gestisce una richiesta riuscita"""
        async with self._lock:
            self.total_successes += 1
            self.failure_count = 0
            
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                
                if self.success_count >= self.success_threshold:
                    await self._transition_to_closed()
                    
            logger.debug(
                "Circuit breaker success",
                service=self.service_name,
                state=self.state.value,
                success_count=self.success_count
            )
    
    async def _on_failure(self, error: Exception):
        """Gestisce una richiesta fallita"""
        async with self._lock:
            self.total_failures += 1
            self.failure_count += 1
            self.success_count = 0
            self.last_failure_time = time.time()
            
            logger.warning(
                "Circuit breaker failure",
                service=self.service_name,
                state=self.state.value,
                failure_count=self.failure_count,
                error=str(error)
            )
            
            if self.state == CircuitState.HALF_OPEN:
                # Fallimento durante test di recupero
                await self._transition_to_open()
                
            elif (self.state == CircuitState.CLOSED and 
                  self.failure_count >= self.failure_threshold):
                # Troppi fallimenti, apri il circuito
                await self._transition_to_open()
    
    async def _transition_to_open(self):
        """Transizione allo stato OPEN"""
        if self.state != CircuitState.OPEN:
            self.state = CircuitState.OPEN
            self.next_attempt_time = time.time() + self.recovery_timeout
            self.state_changes += 1
            
            logger.error(
                "Circuit breaker opened",
                service=self.service_name,
                failure_count=self.failure_count,
                recovery_timeout=self.recovery_timeout
            )
    
    async def _transition_to_half_open(self):
        """Transizione allo stato HALF_OPEN"""
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
        self.state_changes += 1
        
        logger.info(
            "Circuit breaker half-open, testing recovery",
            service=self.service_name
        )
    
    async def _transition_to_closed(self):
        """Transizione allo stato CLOSED"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.next_attempt_time = None
        self.state_changes += 1
        
        logger.info(
            "Circuit breaker closed, service recovered",
            service=self.service_name
        )
    
    def _seconds_until_retry(self) -> int:
        """Calcola secondi rimanenti prima del prossimo tentativo"""
        if not self.next_attempt_time:
            return 0
        
        remaining = self.next_attempt_time - time.time()
        return max(0, int(remaining))
    
    def get_stats(self) -> dict:
        """Ottieni statistiche del circuit breaker"""
        uptime_seconds = time.time() - (self.last_failure_time or time.time())
        
        return {
            "service": self.service_name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "total_requests": self.total_requests,
            "total_failures": self.total_failures,
            "total_successes": self.total_successes,
            "state_changes": self.state_changes,
            "failure_rate": (
                self.total_failures / self.total_requests 
                if self.total_requests > 0 else 0
            ),
            "uptime_seconds": uptime_seconds,
            "next_attempt_in_seconds": self._seconds_until_retry() if self.state == CircuitState.OPEN else None,
            "configuration": {
                "failure_threshold": self.failure_threshold,
                "recovery_timeout": self.recovery_timeout,
                "success_threshold": self.success_threshold
            }
        }
    
    async def force_open(self):
        """Forza l'apertura del circuito (per testing/maintenance)"""
        async with self._lock:
            await self._transition_to_open()
            logger.warning(f"Circuit breaker manually opened for {self.service_name}")
    
    async def force_close(self):
        """Forza la chiusura del circuito (per testing/maintenance)"""
        async with self._lock:
            await self._transition_to_closed()
            logger.info(f"Circuit breaker manually closed for {self.service_name}")
    
    async def reset(self):
        """Reset completo del circuit breaker"""
        async with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            self.next_attempt_time = None
            self.total_requests = 0
            self.total_failures = 0
            self.total_successes = 0
            self.state_changes = 0
            
            logger.info(f"Circuit breaker reset for {self.service_name}")

# Registry globale dei circuit breaker
_circuit_breakers: dict[str, CircuitBreaker] = {}

def get_circuit_breaker(
    service_name: str,
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    success_threshold: int = 2
) -> CircuitBreaker:
    """
    Ottieni o crea un circuit breaker per un servizio
    
    Args:
        service_name: Nome del servizio
        failure_threshold: Soglia fallimenti
        recovery_timeout: Timeout recupero
        success_threshold: Soglia successi
        
    Returns:
        Istanza CircuitBreaker
    """
    if service_name not in _circuit_breakers:
        _circuit_breakers[service_name] = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            success_threshold=success_threshold,
            service_name=service_name
        )
    
    return _circuit_breakers[service_name]

def get_all_circuit_breaker_stats() -> dict:
    """Ottieni statistiche di tutti i circuit breaker"""
    return {
        name: cb.get_stats() 
        for name, cb in _circuit_breakers.items()
    }

class CircuitBreakerRegistry:
    """
    Registry per gestire e monitorare tutti i circuit breaker del sistema
    """
    
    @staticmethod
    def get_stats(service_name: str) -> dict:
        """
        Ottieni statistiche per un circuit breaker specifico
        
        Args:
            service_name: Nome del servizio
            
        Returns:
            Dict con statistiche del circuit breaker
        """
        circuit_breaker = _circuit_breakers.get(service_name)
        if circuit_breaker:
            return circuit_breaker.get_stats()
        
        return {
            "service": service_name,
            "state": "NOT_FOUND",
            "total_requests": 0,
            "total_failures": 0,
            "total_successes": 0,
            "failure_count": 0,
            "success_count": 0,
            "state_changes": 0,
            "last_failure_time": None,
            "next_attempt_time": None
        }
    
    @staticmethod
    def get_all_stats() -> dict:
        """
        Ottieni statistiche per tutti i circuit breaker registrati
        
        Returns:
            Dict con nome servizio come chiave e statistiche come valore
        """
        return get_all_circuit_breaker_stats()
    
    @staticmethod
    def list_services() -> list:
        """
        Lista tutti i servizi con circuit breaker registrati
        
        Returns:
            Lista dei nomi dei servizi
        """
        return list(_circuit_breakers.keys())
    
    @staticmethod
    def is_service_healthy(service_name: str) -> bool:
        """
        Verifica se un servizio è healthy (circuit breaker closed)
        
        Args:
            service_name: Nome del servizio
            
        Returns:
            True se il servizio è healthy
        """
        circuit_breaker = _circuit_breakers.get(service_name)
        if not circuit_breaker:
            return False
            
        return circuit_breaker.state == CircuitState.CLOSED
    
    @staticmethod
    def get_open_circuits() -> list:
        """
        Ottieni lista dei circuit breaker aperti
        
        Returns:
            Lista dei nomi dei servizi con circuit breaker aperto
        """
        open_circuits = []
        for name, cb in _circuit_breakers.items():
            if cb.state == CircuitState.OPEN:
                open_circuits.append(name)
        return open_circuits
    
    @staticmethod
    def reset_circuit(service_name: str) -> bool:
        """
        Reset manuale di un circuit breaker
        
        Args:
            service_name: Nome del servizio
            
        Returns:
            True se il reset è avvenuto con successo
        """
        circuit_breaker = _circuit_breakers.get(service_name)
        if circuit_breaker:
            asyncio.create_task(circuit_breaker.reset())
            return True
        return False 