import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

def get_engine():
    db_url = settings.sync_database_url
    connect_args = {}
    engine_kwargs = {
        "echo": False, # Keep seed and run logs clean
    }

    if db_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        engine_kwargs["connect_args"] = connect_args
        return create_engine(db_url, **engine_kwargs)
    else:
        # PostgreSQL production configuration
        engine_kwargs["pool_pre_ping"] = True
        engine_kwargs["pool_size"] = 10
        engine_kwargs["max_overflow"] = 20
        engine_kwargs["pool_recycle"] = 1800
        try:
            eng = create_engine(db_url, **engine_kwargs)
            # Eagerly probe connection to verify Postgres daemon is accepting connections
            with eng.connect() as conn:
                pass
            return eng
        except Exception as exc:
            print(f"\n[Database Warning] PostgreSQL not reachable at {db_url}.")
            print(f"[Database Notice] Automatically using local SQLite fallback (pos_local.db).")
            return create_engine("sqlite:///./pos_local.db", connect_args={"check_same_thread": False})

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI dependency yielding database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
