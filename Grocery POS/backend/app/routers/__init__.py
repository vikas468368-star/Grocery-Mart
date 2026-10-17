from fastapi import APIRouter
from .health import router as health_router
from .auth import router as auth_router
from .products import router as products_router
from .orders import router as orders_router
from .billing import router as billing_router
from .customers import router as customers_router
from .categories import router as categories_router
from .users import router as users_router
from .reports import router as reports_router
from .settings import router as settings_router
from .suppliers import router as suppliers_router
from .payments import router as payments_router
from .returns import router as returns_router
from .sales import router as sales_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(products_router)
api_router.include_router(orders_router)
api_router.include_router(billing_router)
api_router.include_router(customers_router)
api_router.include_router(categories_router)
api_router.include_router(users_router)
api_router.include_router(reports_router)
api_router.include_router(settings_router)
api_router.include_router(suppliers_router)
api_router.include_router(payments_router)
api_router.include_router(returns_router)
api_router.include_router(sales_router)

__all__ = ["api_router"]
