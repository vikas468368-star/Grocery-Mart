from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.core.auth import require_manager
from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])

def _format_product(product: Product) -> dict:
    data = {
        "id": product.id,
        "name": product.name,
        "barcode": product.barcode,
        "sku": product.sku,
        "category_id": product.category_id,
        "category_name": product.category.name if product.category else "General",
        "supplier_id": product.supplier_id,
        "description": product.description,
        "price": product.price,
        "cost_price": product.cost_price,
        "stock_quantity": product.stock_quantity,
        "min_stock_alert": product.min_stock_alert,
        "unit": product.unit,
        "tax_rate": product.tax_rate,
        "expiry_date": product.expiry_date,
        "batch_number": product.batch_number,
        "is_active": product.is_active,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
    }
    return data

@router.get("/", response_model=List[ProductResponse])
def get_products(
    search: Optional[str] = Query(None, description="Search by name, barcode, or SKU"),
    category: Optional[str] = Query(None, description="Filter by category name"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    skip: int = 0,
    limit: int = 700,
    db: Session = Depends(get_db)
):
    """Retrieve all grocery products with optional search, category filters, and expiry tracking."""
    query = db.query(Product).options(joinedload(Product.category)).filter(Product.is_active == True)

    if search:
        query = query.filter(
            (Product.name.ilike(f"%{search}%")) |
            (Product.barcode.ilike(f"%{search}%")) |
            (Product.sku.ilike(f"%{search}%"))
        )
    if category_id:
        query = query.filter(Product.category_id == category_id)
    elif category and category != "All":
        query = query.join(Product.category).filter(Category.name.ilike(f"%{category}%"))

    products = query.order_by(Product.name.asc()).offset(skip).limit(limit).all()
    return [_format_product(p) for p in products]

@router.get("/barcode/{barcode}", response_model=ProductResponse)
def get_product_by_barcode(barcode: str, db: Session = Depends(get_db)):
    """Instant lookup by barcode scanner gun or manual entry."""
    product = db.query(Product).options(joinedload(Product.category)).filter(Product.barcode == barcode, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with barcode '{barcode}' not found")
    return _format_product(product)

@router.get("/low-stock", response_model=List[ProductResponse])
def get_low_stock_products(
    threshold: Optional[float] = Query(None, description="Optional custom stock threshold. If omitted, uses each product's min_stock_alert."),
    db: Session = Depends(get_db)
):
    """Retrieve products running low on stock (stock <= min_stock_alert or custom threshold)."""
    query = db.query(Product).options(joinedload(Product.category)).filter(Product.is_active == True)
    if threshold is not None:
        query = query.filter(Product.stock_quantity <= threshold)
    else:
        query = query.filter(Product.stock_quantity <= Product.min_stock_alert)
    
    products = query.order_by(Product.stock_quantity.asc()).all()
    return [_format_product(p) for p in products]

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product details by ID."""
    product = db.query(Product).options(joinedload(Product.category)).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return _format_product(product)

@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(
    product_in: ProductCreate,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Create a new product item in the inventory catalog. Restricted to Managers and Owners."""
    existing = db.query(Product).filter(Product.barcode == product_in.barcode).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product with this barcode already exists")

    product = Product(**product_in.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return _format_product(product)

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Update product information or inventory quantity. Restricted to Managers and Owners."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(product, field, val)

    db.commit()
    db.refresh(product)
    return _format_product(product)

@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Soft-delete product by marking inactive. Restricted to Managers and Owners."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = False
    db.commit()
    return None
