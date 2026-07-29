"""
Customer API routes — v1.

All endpoints follow RESTful conventions and return consistent
JSON envelopes via the service layer.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    DeleteResponse,
    PaginatedCustomerResponse,
    SingleCustomerResponse,
)
from app.services.customer_service import CustomerService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/customers", tags=["Customers"])


def _get_service(db: Session = Depends(get_db)) -> CustomerService:
    """FastAPI dependency that injects a CustomerService."""
    return CustomerService(db)


# ── POST /api/v1/customers ───────────────────────────────────────────────────


@router.post(
    "",
    response_model=SingleCustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new customer",
    description=(
        "Register a new lending customer. "
        "Email and phone must be unique across all customers."
    ),
)
def create_customer(
    payload: CustomerCreate,
    service: CustomerService = Depends(_get_service),
) -> SingleCustomerResponse:
    logger.info("POST /api/v1/customers — email=%s", payload.email)
    return service.create_customer(payload)


# ── GET /api/v1/customers ────────────────────────────────────────────────────


@router.get(
    "",
    response_model=PaginatedCustomerResponse,
    summary="List customers (paginated)",
    description=(
        "Retrieve a paginated list of customers. "
        "Supports optional search by email, phone, or name."
    ),
)
def list_customers(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    email: Optional[str] = Query(None, description="Search by email (partial match)"),
    phone: Optional[str] = Query(None, description="Search by phone (partial match)"),
    name: Optional[str] = Query(None, description="Search by first or last name (partial match)"),
    service: CustomerService = Depends(_get_service),
) -> PaginatedCustomerResponse:
    logger.info(
        "GET /api/v1/customers — page=%d limit=%d email=%s phone=%s name=%s",
        page, limit, email, phone, name,
    )
    return service.list_customers(
        page=page, limit=limit, email=email, phone=phone, name=name
    )


# ── GET /api/v1/customers/{id} ──────────────────────────────────────────────


@router.get(
    "/{customer_id}",
    response_model=SingleCustomerResponse,
    summary="Get a customer by ID",
    description="Retrieve a single customer record by its UUID.",
)
def get_customer(
    customer_id: UUID,
    service: CustomerService = Depends(_get_service),
) -> SingleCustomerResponse:
    logger.info("GET /api/v1/customers/%s", customer_id)
    return service.get_customer(customer_id)


# ── PUT /api/v1/customers/{id} ──────────────────────────────────────────────


@router.put(
    "/{customer_id}",
    response_model=SingleCustomerResponse,
    summary="Update a customer",
    description=(
        "Partially update a customer record. "
        "Only the fields provided in the request body are modified."
    ),
)
def update_customer(
    customer_id: UUID,
    payload: CustomerUpdate,
    service: CustomerService = Depends(_get_service),
) -> SingleCustomerResponse:
    logger.info("PUT /api/v1/customers/%s", customer_id)
    return service.update_customer(customer_id, payload)


# ── DELETE /api/v1/customers/{id} ───────────────────────────────────────────


@router.delete(
    "/{customer_id}",
    response_model=DeleteResponse,
    summary="Delete a customer",
    description="Permanently remove a customer record by its UUID.",
)
def delete_customer(
    customer_id: UUID,
    service: CustomerService = Depends(_get_service),
) -> DeleteResponse:
    logger.info("DELETE /api/v1/customers/%s", customer_id)
    return service.delete_customer(customer_id)
