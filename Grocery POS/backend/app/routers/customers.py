from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerResponse

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("/", response_model=List[CustomerResponse])
def get_customers(
    phone: Optional[str] = Query(None, description="Lookup by phone number"),
    db: Session = Depends(get_db)
):
    """Retrieve customers or search by mobile number."""
    if phone:
        customer = db.query(Customer).filter(Customer.phone == phone).first()
        return [customer] if customer else []
    return db.query(Customer).all()

@router.post("/", response_model=CustomerResponse, status_code=201)
def create_customer(customer_in: CustomerCreate, db: Session = Depends(get_db)):
    """Register a new customer for loyalty rewards and receipts."""
    if customer_in.phone:
        existing = db.query(Customer).filter(Customer.phone == customer_in.phone).first()
        if existing:
            raise HTTPException(status_code=400, detail="Customer with this phone number already exists")

    customer = Customer(**customer_in.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer
