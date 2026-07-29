"""
Customer repository — data-access layer.

Encapsulates all database queries for the Customer entity,
keeping SQL logic isolated from the service layer.
"""

import logging
import math
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.utils.exceptions import ConflictException, NotFoundException

logger = logging.getLogger(__name__)


class CustomerRepository:
    """Repository for Customer CRUD and query operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── CREATE ───────────────────────────────────────────────────────────

    def create(self, payload: CustomerCreate) -> Customer:
        """
        Persist a new customer.

        Raises:
            ConflictException: If email or phone already exists.
        """
        customer = Customer(**payload.model_dump())
        try:
            self.db.add(customer)
            self.db.commit()
            self.db.refresh(customer)
            logger.info("Created customer id=%s email=%s", customer.id, customer.email)
            return customer
        except IntegrityError as exc:
            self.db.rollback()
            error_detail = str(exc.orig).lower() if exc.orig else ""
            if "email" in error_detail:
                raise ConflictException(
                    f"A customer with email '{payload.email}' already exists"
                ) from exc
            if "phone" in error_detail:
                raise ConflictException(
                    f"A customer with phone '{payload.phone}' already exists"
                ) from exc
            raise ConflictException(
                "A customer with the provided details already exists"
            ) from exc

    # ── READ (single) ────────────────────────────────────────────────────

    def get_by_id(self, customer_id: UUID) -> Customer:
        """
        Fetch a single customer by UUID.

        Raises:
            NotFoundException: If the customer does not exist.
        """
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        if customer is None:
            logger.warning("Customer not found: id=%s", customer_id)
            raise NotFoundException(f"Customer not found with id: {customer_id}")
        return customer

    # ── READ (list + pagination + search) ────────────────────────────────

    def get_all(
        self,
        page: int = 1,
        limit: int = 10,
        search_email: Optional[str] = None,
        search_phone: Optional[str] = None,
        search_name: Optional[str] = None,
    ) -> Tuple[List[Customer], int, int]:
        """
        Return a paginated, optionally filtered list of customers.

        Returns:
            (customers, total_count, total_pages)
        """
        query = self.db.query(Customer)

        # Apply search filters
        if search_email:
            query = query.filter(Customer.email.ilike(f"%{search_email}%"))
        if search_phone:
            query = query.filter(Customer.phone.ilike(f"%{search_phone}%"))
        if search_name:
            pattern = f"%{search_name}%"
            query = query.filter(
                or_(
                    Customer.first_name.ilike(pattern),
                    Customer.last_name.ilike(pattern),
                )
            )

        total = query.count()
        total_pages = max(1, math.ceil(total / limit))
        offset = (page - 1) * limit

        customers = (
            query
            .order_by(Customer.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        logger.info(
            "Listed customers page=%d limit=%d total=%d filters(email=%s phone=%s name=%s)",
            page, limit, total, search_email, search_phone, search_name,
        )
        return customers, total, total_pages

    # ── UPDATE ───────────────────────────────────────────────────────────

    def update(self, customer_id: UUID, payload: CustomerUpdate) -> Customer:
        """
        Partially update an existing customer.

        Raises:
            NotFoundException: If the customer does not exist.
            ConflictException: If email/phone conflicts with another record.
        """
        customer = self.get_by_id(customer_id)
        update_data: Dict = payload.model_dump(exclude_unset=True)

        if not update_data:
            return customer

        for field, value in update_data.items():
            setattr(customer, field, value)

        try:
            self.db.commit()
            self.db.refresh(customer)
            logger.info("Updated customer id=%s fields=%s", customer_id, list(update_data.keys()))
            return customer
        except IntegrityError as exc:
            self.db.rollback()
            error_detail = str(exc.orig).lower() if exc.orig else ""
            if "email" in error_detail:
                raise ConflictException(
                    f"A customer with email '{update_data.get('email')}' already exists"
                ) from exc
            if "phone" in error_detail:
                raise ConflictException(
                    f"A customer with phone '{update_data.get('phone')}' already exists"
                ) from exc
            raise ConflictException(
                "Update conflicts with an existing customer record"
            ) from exc

    # ── DELETE ───────────────────────────────────────────────────────────

    def delete(self, customer_id: UUID) -> None:
        """
        Delete a customer by UUID.

        Raises:
            NotFoundException: If the customer does not exist.
        """
        customer = self.get_by_id(customer_id)
        self.db.delete(customer)
        self.db.commit()
        logger.info("Deleted customer id=%s", customer_id)
