from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    barcode = Column(String(100), unique=True, index=True, nullable=False)
    sku = Column(String(100), unique=True, index=True, nullable=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True, index=True)

    # Pricing & Stock
    price = Column(Float, nullable=False)              # Retail Selling price
    cost_price = Column(Float, default=0.0, nullable=False) # Wholesale / Purchase cost
    stock_quantity = Column(Float, default=0.0, nullable=False) # Allows decimal quantities for fruits/vegetables/grains
    min_stock_alert = Column(Float, default=10.0)      # Low stock threshold
    unit = Column(String(20), default="pcs", nullable=False) # pcs, kg, g, pack, L, bottle
    tax_rate = Column(Float, default=0.05, nullable=False)   # e.g., 0.05 (5%), 0.12 (12%), 0.18 (18%)

    # Product Freshness & Batch Management
    expiry_date = Column(Date, nullable=True, index=True)
    batch_number = Column(String(50), nullable=True)

    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    sale_items = relationship("SaleItem", back_populates="product")
    purchase_order_items = relationship("PurchaseOrderItem", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', barcode='{self.barcode}', stock={self.stock_quantity})>"
