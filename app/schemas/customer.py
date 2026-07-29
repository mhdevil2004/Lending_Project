"""
Pydantic v2 schemas for Customer request/response validation.

Includes strict validation for email, phone, credit score,
annual income, and loan amount.
"""

import re
import uuid
from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class GenderEnum(str, Enum):
    """Allowed gender values."""
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class EmploymentTypeEnum(str, Enum):
    """Allowed employment type values."""
    SALARIED = "Salaried"
    SELF_EMPLOYED = "Self-Employed"
    BUSINESS = "Business"
    UNEMPLOYED = "Unemployed"
    RETIRED = "Retired"
    STUDENT = "Student"


# ── Phone regex ──────────────────────────────────────────────────────────────
# Accepts formats: +1-234-567-8901, +12345678901, 1234567890, (123) 456-7890
_PHONE_PATTERN = re.compile(
    r"^\+?1?\d{9,15}$|"
    r"^\+?\d{1,4}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$|"
    r"^\(\d{3}\)\s?\d{3}[-.]?\d{4}$"
)


class CustomerBase(BaseModel):
    """Shared fields and validators for customer payloads."""

    first_name: str = Field(
        ..., min_length=1, max_length=100, examples=["Rahul"],
        description="Customer's first name",
    )
    last_name: str = Field(
        ..., min_length=1, max_length=100, examples=["Sharma"],
        description="Customer's last name",
    )
    email: EmailStr = Field(
        ..., examples=["rahul.sharma@example.com"],
        description="Unique email address",
    )
    phone: str = Field(
        ..., min_length=7, max_length=20, examples=["+919876543210"],
        description="Phone number (E.164 or common formats accepted)",
    )
    date_of_birth: date = Field(
        ..., examples=["1990-05-15"],
        description="Date of birth in ISO-8601 format",
    )
    gender: GenderEnum = Field(
        ..., examples=["Male"],
        description="Gender (Male, Female, Other)",
    )
    employment_type: EmploymentTypeEnum = Field(
        ..., examples=["Salaried"],
        description="Type of employment",
    )
    annual_income: float = Field(
        ..., gt=0, examples=[850000.00],
        description="Annual income — must be greater than zero",
    )
    loan_amount: float = Field(
        ..., gt=0, examples=[500000.00],
        description="Requested loan amount — must be greater than zero",
    )
    credit_score: int = Field(
        ..., ge=300, le=900, examples=[750],
        description="Credit score between 300 and 900",
    )
    address: str = Field(
        ..., min_length=1, max_length=500, examples=["42 MG Road"],
        description="Street address",
    )
    city: str = Field(
        ..., min_length=1, max_length=100, examples=["Bengaluru"],
        description="City",
    )
    state: str = Field(
        ..., min_length=1, max_length=100, examples=["Karnataka"],
        description="State or province",
    )
    country: str = Field(
        ..., min_length=1, max_length=100, examples=["India"],
        description="Country",
    )
    postal_code: str = Field(
        ..., min_length=1, max_length=20, examples=["560001"],
        description="Postal / ZIP code",
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        """Ensure the phone number matches an accepted format."""
        cleaned = value.strip()
        if not _PHONE_PATTERN.match(cleaned):
            raise ValueError(
                "Invalid phone number format. "
                "Accepted examples: +919876543210, (123) 456-7890, 1234567890"
            )
        return cleaned

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob_not_future(cls, value: date) -> date:
        """Date of birth must not be in the future."""
        if value > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return value


class CustomerCreate(CustomerBase):
    """Schema for creating a new customer."""
    pass


class CustomerUpdate(BaseModel):
    """Schema for partial customer updates — every field is optional."""

    model_config = ConfigDict(from_attributes=True)

    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=7, max_length=20)
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    employment_type: Optional[EmploymentTypeEnum] = None
    annual_income: Optional[float] = Field(None, gt=0)
    loan_amount: Optional[float] = Field(None, gt=0)
    credit_score: Optional[int] = Field(None, ge=300, le=900)
    address: Optional[str] = Field(None, min_length=1, max_length=500)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=1, max_length=100)
    country: Optional[str] = Field(None, min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, min_length=1, max_length=20)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        if not _PHONE_PATTERN.match(cleaned):
            raise ValueError(
                "Invalid phone number format. "
                "Accepted examples: +919876543210, (123) 456-7890, 1234567890"
            )
        return cleaned

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob_not_future(cls, value: Optional[date]) -> Optional[date]:
        if value is not None and value > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return value


class CustomerResponse(CustomerBase):
    """Schema returned by the API for a single customer."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class PaginatedCustomerResponse(BaseModel):
    """Paginated list response wrapper."""

    success: bool = True
    message: str = "Customers retrieved successfully"
    data: List[CustomerResponse]
    page: int
    limit: int
    total: int
    total_pages: int


class SingleCustomerResponse(BaseModel):
    """Single customer response wrapper."""

    success: bool = True
    message: str = "Customer retrieved successfully"
    data: CustomerResponse


class DeleteResponse(BaseModel):
    """Response after a successful deletion."""

    success: bool = True
    message: str = "Customer deleted successfully"
    status: int = 200
