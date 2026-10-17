from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base

class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    CARD = "CARD"
    UPI = "UPI"
    STORE_CREDIT = "STORE_CREDIT"
    SPLIT = "SPLIT"

class PaymentStatus(str, enum.Enum):
    PAID = "PAID"
    PENDING = "PENDING"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False, index=True)

    payment_method = Column(Enum(PaymentMethod, values_callable=lambda obj: [e.value for e in obj]), default=PaymentMethod.CASH, nullable=False)
    amount = Column(Float, nullable=False)
    tendered_amount = Column(Float, nullable=True) # Useful for cash transactions
    change_amount = Column(Float, default=0.0)      # Cash returned to customer
    transaction_reference = Column(String(100), nullable=True) # Card slip auth or UPI UTR number
    status = Column(Enum(PaymentStatus, values_callable=lambda obj: [e.value for e in obj]), default=PaymentStatus.PAID, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sale = relationship("Sale", back_populates="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, method='{self.payment_method}', amount={self.amount}, status='{self.status}')>"
