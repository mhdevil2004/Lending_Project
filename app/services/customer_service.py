
import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    DeleteResponse,
    PaginatedCustomerResponse,
    CustomerResponse,
    SingleCustomerResponse,
)

logger = logging.getLogger(__name__)


class CustomerService:
    """Service layer for customer operations."""

    def __init__(self, db: Session) -> None:
        self.repository = CustomerRepository(db)

    def create_customer(self, payload: CustomerCreate) -> SingleCustomerResponse:
        """Create a new customer and return a wrapped response."""
        customer: Customer = self.repository.create(payload)
        return SingleCustomerResponse(
            success=True,
            message="Customer created successfully",
            data=CustomerResponse.model_validate(customer),
        )

    def get_customer(self, customer_id: UUID) -> SingleCustomerResponse:
        """Retrieve a single customer by ID."""
        customer: Customer = self.repository.get_by_id(customer_id)
        return SingleCustomerResponse(
            success=True,
            message="Customer retrieved successfully",
            data=CustomerResponse.model_validate(customer),
        )

    def list_customers(
        self,
        page: int = 1,
        limit: int = 10,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        name: Optional[str] = None,
    ) -> PaginatedCustomerResponse:
        """List customers with pagination and optional search filters."""
        customers, total, total_pages = self.repository.get_all(
            page=page,
            limit=limit,
            search_email=email,
            search_phone=phone,
            search_name=name,
        )
        return PaginatedCustomerResponse(
            success=True,
            message="Customers retrieved successfully",
            data=[CustomerResponse.model_validate(c) for c in customers],
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
        )

    def update_customer(
        self, customer_id: UUID, payload: CustomerUpdate
    ) -> SingleCustomerResponse:
        """Update an existing customer (partial)."""
        customer: Customer = self.repository.update(customer_id, payload)
        return SingleCustomerResponse(
            success=True,
            message="Customer updated successfully",
            data=CustomerResponse.model_validate(customer),
        )

    def delete_customer(self, customer_id: UUID) -> DeleteResponse:
        """Delete a customer by ID."""
        self.repository.delete(customer_id)
        return DeleteResponse(
            success=True,
            message="Customer deleted successfully",
            status=200,
        )
