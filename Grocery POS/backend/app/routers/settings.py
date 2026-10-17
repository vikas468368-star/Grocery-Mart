from typing import Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.auth import require_owner
from app.models.user import User

router = APIRouter(prefix="/settings", tags=["Store Settings (Owner Only)"])

class StoreSettingsModel(BaseModel):
    store_name: str = "Grocery Supermarket & HyperMart"
    tagline: str = "Fresh Groceries & Everyday Savings"
    address: str = "Shop 12-14, Central Market Avenue, Vashi Sector 17"
    city: str = "Navi Mumbai"
    state: str = "Maharashtra"
    postal_code: str = "400703"
    gstin: str = "27AABCV1234F1Z9"
    contact_phone: str = "+91 98200 12345"
    contact_email: str = "support@grocerysupermarket.in"
    currency: str = "INR"
    currency_symbol: str = "₹"
    receipt_header: str = "THANK YOU FOR SHOPPING WITH US!"
    receipt_footer: str = "Goods once sold can be returned within 3 days with bill."
    enable_auto_print: bool = True
    default_tax_rate: float = 0.05
    low_stock_threshold: int = 15

# In-memory store settings (can be persisted to database or config)
STORE_SETTINGS: Dict[str, Any] = StoreSettingsModel().dict()

@router.get("/", response_model=Dict[str, Any])
def get_store_settings(current_user: User = Depends(require_owner)):
    """Retrieve store master configuration. Restricted to Store Owner."""
    return {
        **STORE_SETTINGS,
        "configured_by": current_user.full_name,
    }

@router.put("/", response_model=Dict[str, Any])
def update_store_settings(
    settings_data: StoreSettingsModel,
    current_user: User = Depends(require_owner)
):
    """Update store master configuration. Restricted to Store Owner."""
    global STORE_SETTINGS
    STORE_SETTINGS = settings_data.dict()
    return {
        "status": "success",
        "message": "Store configuration successfully updated.",
        "settings": STORE_SETTINGS,
        "updated_by": current_user.full_name,
    }
