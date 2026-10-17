from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    email = Column(String(150), unique=True, index=True, nullable=True)
    loyalty_points = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Supported relationships for both Sales and Orders
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="customer")

    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.name}', phone='{self.phone}')>"
