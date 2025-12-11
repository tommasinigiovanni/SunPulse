"""
Configurazione dell'applicazione SunPulse
"""
from functools import lru_cache
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    """Configurazione dell'applicazione"""
    
    # App Config
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    DEBUG: bool = Field(False, env="DEBUG")
    ENVIRONMENT: str = Field("production", env="ENVIRONMENT")
    
    # Database PostgreSQL
    POSTGRES_HOST: str = Field("localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(5432, env="POSTGRES_PORT")
    POSTGRES_DB: str = Field("sunpulse", env="POSTGRES_DB")
    POSTGRES_USER: str = Field("postgres", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")
    
    # InfluxDB
    INFLUXDB_HOST: str = Field("localhost", env="INFLUXDB_HOST")
    INFLUXDB_PORT: int = Field(8086, env="INFLUXDB_PORT")
    INFLUXDB_DB: str = Field("solar_metrics", env="INFLUXDB_DB")
    INFLUXDB_USER: str = Field("solar_user", env="INFLUXDB_USER")
    INFLUXDB_PASSWORD: str = Field(..., env="INFLUXDB_PASSWORD")
    
    # Redis
    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_PASSWORD: Optional[str] = Field(None, env="REDIS_PASSWORD")
    
    # MQTT
    MQTT_HOST: str = Field("localhost", env="MQTT_HOST")
    MQTT_PORT: int = Field(1883, env="MQTT_PORT")
    
    # ZCS API Configuration
    ZCS_API_URL: str = Field(
        default="https://third.zcsazzurroportal.com:19003/",
        env="ZCS_API_URL",
        description="ZCS Azzurro Portal API base URL"
    )
    ZCS_API_AUTH: str = Field(..., env="ZCS_API_AUTH", description="ZCS API Authorization header")
    ZCS_CLIENT_CODE: str = Field(..., env="ZCS_CLIENT_CODE", description="ZCS API client code")
    ZCS_API_TIMEOUT: int = Field(30, env="ZCS_API_TIMEOUT", description="Request timeout seconds")
    ZCS_API_RATE_LIMIT: int = Field(100, env="ZCS_API_RATE_LIMIT", description="Requests per hour")
    
    # ZCS Device Configuration
    ZCS_DEVICE_KEYS: str = Field(
        default="ZE1ES330J9E558", 
        env="ZCS_DEVICE_KEYS", 
        description="Comma-separated list of device thingKeys"
    )
    
    # Auth0
    AUTH0_DOMAIN: str = Field(..., env="AUTH0_DOMAIN")
    AUTH0_CLIENT_ID: str = Field(..., env="AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET: str = Field(..., env="AUTH0_CLIENT_SECRET")
    
    @property
    def database_url(self) -> str:
        """URL del database PostgreSQL"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def influxdb_url(self) -> str:
        """URL di InfluxDB"""
        return f"http://{self.INFLUXDB_HOST}:{self.INFLUXDB_PORT}"
    
    @property
    def redis_url(self) -> str:
        """URL di Redis"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    @property
    def device_thing_keys(self) -> List[str]:
        """Lista delle thingKey dei dispositivi"""
        return [key.strip() for key in self.ZCS_DEVICE_KEYS.split(",") if key.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Ottieni le impostazioni (con cache)"""
    return Settings() 