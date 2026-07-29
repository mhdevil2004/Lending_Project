

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Customer(Base):
    """ORM model for lending customers."""

    __tablename__ = "customers"

    id: uuid.UUID = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    first_name: str = Column(String(100), nullable=False, index=True)
    last_name: str = Column(String(100), nullable=False, index=True)
    email: str = Column(String(255), nullable=False, unique=True, index=True)
    phone: str = Column(String(20), nullable=False, unique=True, index=True)
    date_of_birth: date = Column(Date, nullable=False)
    gender: str = Column(String(20), nullable=False)
    employment_type: str = Column(String(50), nullable=False)
    annual_income: float = Column(Float, nullable=False)
    loan_amount: float = Column(Float, nullable=False)
    credit_score: int = Column(Integer, nullable=False)
    address: str = Column(String(500), nullable=False)
    city: str = Column(String(100), nullable=False)
    state: str = Column(String(100), nullable=False)
    country: str = Column(String(100), nullable=False)
    postal_code: str = Column(String(20), nullable=False)
    created_at: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: datetime = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Customer {self.first_name} {self.last_name} ({self.email})>"
