"""
Database Dependency Injection for FastAPI

Provides database session dependencies for endpoints.
This module bridges the async database service with FastAPI's dependency injection.
"""
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator
import structlog

from .config.settings import get_settings
from .models.device import Base

logger = structlog.get_logger()

# Synchronous SQLAlchemy Engine (for FastAPI Depends)
_engine = None
_SessionLocal = None


def init_sync_db():
    """
    Initialize synchronous database engine and session factory

    This is used for FastAPI dependency injection with Depends()
    which doesn't support async context managers well.
    """
    global _engine, _SessionLocal

    if _engine is None:
        settings = get_settings()

        # Create synchronous engine
        _engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            echo=False,
        )

        # Create tables if they don't exist
        Base.metadata.create_all(bind=_engine)
        logger.info("Synchronous database engine initialized and tables created")

        # Create session factory
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=_engine
        )


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database session

    Usage in endpoints:
        @router.get("/devices")
        def get_devices(db: Session = Depends(get_db)):
            devices = db.query(Device).all()
            return devices

    Yields:
        Session: SQLAlchemy database session
    """
    global _SessionLocal

    if _SessionLocal is None:
        init_sync_db()

    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


def close_sync_db():
    """Close synchronous database engine"""
    global _engine, _SessionLocal

    if _engine:
        _engine.dispose()
        _engine = None
        _SessionLocal = None
        logger.info("Synchronous database engine closed")
