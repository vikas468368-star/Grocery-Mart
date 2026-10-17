from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import generate_invoice_number
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.customer import Customer
from app.schemas.order import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("/", response_model=List[OrderResponse])
def get_orders(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve history of POS transactions and receipts."""
    return db.query(Order).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Retrieve specific order invoice details."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/checkout", response_model=OrderResponse, status_code=201)
def checkout(order_in: OrderCreate, db: Session = Depends(get_db)):
    """Process POS checkout transaction, decrement inventory stock, and generate receipt invoice."""
    if not order_in.items:
        raise HTTPException(status_code=400, detail="Cannot checkout an empty cart")

    subtotal = 0.0
    total_tax = 0.0

    order_items_entities = []

    # Verify stock availability for all items before processing
    product_map = {}
    for item in order_in.items:
        if item.product_id:
            prod = db.query(Product).filter(Product.id == item.product_id).first()
            if not prod or not prod.is_active:
                raise HTTPException(status_code=400, detail=f"Product '{item.product_name}' is unavailable")
            if prod.stock_quantity < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for '{prod.name}'. Available: {prod.stock_quantity} {prod.unit}, requested: {item.quantity} {prod.unit}"
                )
            product_map[item.product_id] = prod

    for item in order_in.items:
        line_subtotal = item.unit_price * item.quantity
        line_tax = line_subtotal * item.tax_rate
        line_total = line_subtotal + line_tax - item.discount_amount
        
        subtotal += line_subtotal
        total_tax += line_tax

        # Decrement product inventory
        prod = product_map.get(item.product_id)
        if prod:
            prod.stock_quantity = max(0.0, prod.stock_quantity - item.quantity)

        order_item = OrderItem(
            product_id=item.product_id,
            product_name=item.product_name,
            unit_price=item.unit_price,
            quantity=item.quantity,
            unit=item.unit,
            tax_rate=item.tax_rate,
            tax_amount=line_tax,
            discount_amount=item.discount_amount,
            total=line_total,
        )
        order_items_entities.append(order_item)

    grand_total = subtotal + total_tax - order_in.discount_amount

    # Create Order
    order = Order(
        invoice_number=generate_invoice_number(),
        cashier_name=order_in.cashier_name or "Cashier 1",
        customer_id=order_in.customer_id,
        subtotal=round(subtotal, 2),
        tax_amount=round(total_tax, 2),
        discount_amount=round(order_in.discount_amount, 2),
        total_amount=round(grand_total, 2),
        payment_method=order_in.payment_method,
        payment_status="COMPLETED",
        notes=order_in.notes,
        items=order_items_entities,
    )

    # Update customer loyalty points if customer associated
    if order_in.customer_id:
        cust = db.query(Customer).filter(Customer.id == order_in.customer_id).first()
        if cust:
            cust.total_spent += grand_total
            cust.loyalty_points += int(grand_total // 10) # 1 point per $10/Rs10

    db.add(order)
    db.commit()
    db.refresh(order)
    return order
