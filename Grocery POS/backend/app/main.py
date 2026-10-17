from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.routers import api_router
from app.models import Product, Category, User, Supplier
from app.seeds.seed_data import seed_database

# Initialize database schema tables
Base.metadata.create_all(bind=engine)
try:
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE sale_items ADD COLUMN returned_quantity FLOAT DEFAULT 0.0"))
        conn.commit()
except Exception:
    pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="High-performance backend API for Grocery Store POS Billing System with real-time barcode lookup, stock management, multi-role users, and invoice generation.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Configure CORS for React frontend & Electron desktop
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include main router
app.include_router(api_router, prefix=settings.API_V1_STR)

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join([str(loc) for loc in error.get("loc", []) if loc != "body"])
        errors.append({
            "field": field or "payload",
            "message": error.get("msg", "Invalid value"),
            "type": error.get("type", "validation_error")
        })
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error in request payload",
            "errors": errors
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def global_unhandled_exception_handler(request, exc: Exception):
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error occurred while processing the request",
            "error_type": type(exc).__name__,
            "message": str(exc)
        }
    )

@app.on_event("startup")
def verify_and_seed_catalog():
    """Ensure database has the 500+ grocery catalog records and all table columns on launch."""
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE sale_items ADD COLUMN returned_quantity FLOAT DEFAULT 0.0"))
            conn.commit()
    except Exception:
        pass

    db = SessionLocal()
    try:
        count = db.query(Product).count()
        if count < 500:
            print(f"[Startup] Found {count} products in DB. Running 500+ grocery catalog seeder...")
            seed_database()
        else:
            print(f"[Startup] Database catalog verified with {count} grocery products.")
    except Exception as e:
        print(f"[Startup Warning] Seeding check: {e}")
    finally:
        db.close()

@app.get("/")
def root():
    return {
        "app": settings.PROJECT_NAME,
        "status": "online",
        "docs_url": f"{settings.API_V1_STR}/docs",
        "api_v1": settings.API_V1_STR,
    }
