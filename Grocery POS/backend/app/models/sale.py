from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base

class SaleStatus(str, enum.Enum):
    PAID = "Paid"
    COMPLETED = "COMPLETED"
    PENDING = "PENDING"
    REFUNDED = "REFUNDED"
    VOID = "VOID"

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, index=True, nullable=False)
    cashier_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)

    customer_name = Column(String(150), default="Walk-in Customer")
    customer_phone = Column(String(20), nullable=True, index=True)

    # Financial Breakdowns
    subtotal = Column(Float, default=0.0, nullable=False)
    tax_amount = Column(Float, default=0.0, nullable=False)
    discount_amount = Column(Float, default=0.0, nullable=False)
    grand_total = Column(Float, default=0.0, nullable=False)

    status = Column(Enum(SaleStatus, values_callable=lambda obj: [e.value for e in obj]), default=SaleStatus.COMPLETED, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    cashier = relationship("User", back_populates="sales")
    customer = relationship("Customer", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="sale", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sale(id={self.id}, invoice='{self.invoice_number}', total={self.grand_total})>"

class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)

    # Snapshot of item at time of transaction
    product_name = Column(String(255), nullable=False)
    barcode = Column(String(100), nullable=True, index=True)
    quantity = Column(Float, default=1.0, nullable=False)
    unit = Column(String(20), default="pcs", nullable=False)
    unit_price = Column(Float, nullable=False)
    cost_price = Column(Float, default=0.0)
    tax_rate = Column(Float, default=0.05)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    line_total = Column(Float, nullable=False)
    returned_quantity = Column(Float, default=0.0, nullable=False)

    # Relationships
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")

    def __repr__(self):
        return f"<SaleItem(id={self.id}, product='{self.product_name}', qty={self.quantity}, total={self.line_total})>"

class SaleReturn(Base):
    __tablename__ = "sale_returns"

    id = Column(Integer, primary_key=True, index=True)
    return_number = Column(String(50), unique=True, index=True, nullable=False)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False, index=True)
    refund_amount = Column(Float, nullable=False)
    refund_method = Column(String(50), default="CASH", nullable=False)
    reason = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    sale = relationship("Sale", backref="returns")
    items = relationship("ReturnItem", back_populates="sale_return", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SaleReturn(id={self.id}, number='{self.return_number}', refund={self.refund_amount})>"

class ReturnItem(Base):
    __tablename__ = "return_items"

    id = Column(Integer, primary_key=True, index=True)
    return_id = Column(Integer, ForeignKey("sale_returns.id", ondelete="CASCADE"), nullable=False, index=True)
    sale_item_id = Column(Integer, ForeignKey("sale_items.id", ondelete="SET NULL"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), default="pcs")
    refund_unit_price = Column(Float, nullable=False)
    refund_subtotal = Column(Float, nullable=False)
    reason = Column(String(255), nullable=True)

    sale_return = relationship("SaleReturn", back_populates="items")

    def __repr__(self):
        return f"<ReturnItem(id={self.id}, product='{self.product_name}', qty={self.quantity})>"

