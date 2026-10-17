from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import require_manager
from app.models.category import Category
from app.models.user import User
from pydantic import BaseModel, Field

router = APIRouter(prefix="/categories", tags=["Categories & Departments"])

from pydantic import BaseModel, Field, field_validator

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, example="Dairy & Eggs")
    code: str = Field(..., min_length=1, example="CAT-DAIRY")
    icon: Optional[str] = Field(None, example="dairy")
    default_tax_rate: float = Field(0.05, ge=0.0, le=1.0, example=0.05)
    description: Optional[str] = Field(None, example="Fresh milk, butter, cheese, and farm eggs")
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Category name cannot be empty")
        return s

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        s = v.strip().upper()
        if not s:
            raise ValueError("Category code cannot be empty")
        return s

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    icon: Optional[str] = None
    default_tax_rate: Optional[float] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True

@router.get("/", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Retrieve all grocery departments and categories."""
    return db.query(Category).filter(Category.is_active == True).order_by(Category.name.asc()).all()

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a single category."""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    cat_in: CategoryCreate,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Create a new department/category. Restricted to Managers and Owners."""
    existing = db.query(Category).filter(Category.code == cat_in.code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Category with code '{cat_in.code}' already exists")
    
    cat = Category(**cat_in.dict())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    cat_in: CategoryUpdate,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Update department/category details. Restricted to Managers and Owners."""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = cat_in.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(cat, field, val)
    
    db.commit()
    db.refresh(cat)
    return cat

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    current_user: User = Depends(require_manager),
    db: Session = Depends(get_db)
):
    """Soft-delete category. Restricted to Managers and Owners."""
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    
    cat.is_active = False
    db.commit()
    return None
