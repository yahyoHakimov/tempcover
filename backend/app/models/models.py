"""
TempCover Insurance Platform
SQLAlchemy ORM Models — PostgreSQL
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, String, Boolean, DateTime, Date,   # ← Date qo'shildi
    ForeignKey, Numeric, Integer, Text, Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


# ─────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────

class UserRole(str, PyEnum):
    SUPER_ADMIN = "super_admin"
    ADMIN       = "admin"
    USER        = "user"


class TenantPlan(str, PyEnum):
    BASIC      = "basic"
    PRO        = "pro"
    ENTERPRISE = "enterprise"


class TenantStatus(str, PyEnum):
    ACTIVE    = "active"
    SUSPENDED = "suspended"
    PENDING   = "pending"
    EXPIRED   = "expired"


class PolicyStatus(str, PyEnum):
    ACTIVE    = "active"
    EXPIRED   = "expired"
    CANCELLED = "cancelled"
    PENDING   = "pending"


class DurationType(str, PyEnum):
    HOURLY = "hourly"
    DAILY  = "daily"


class CoverType(str, PyEnum):
    FULLY_COMPREHENSIVE    = "fully_comprehensive"
    THIRD_PARTY_FIRE_THEFT = "third_party_fire_theft"
    THIRD_PARTY_ONLY       = "third_party_only"


class VehicleValueRange(str, PyEnum):
    RANGE_0_10000      = "£0-10000"
    RANGE_10001_25000  = "£10001-25000"
    RANGE_25001_50000  = "£25001-50000"
    RANGE_50001_75000  = "£50001-75000"
    RANGE_75001_100000 = "£75001-100000"
    RANGE_100000_PLUS  = "£100000+"


class PaymentStatus(str, PyEnum):
    PENDING  = "pending"
    SUCCESS  = "success"
    FAILED   = "failed"
    REFUNDED = "refunded"


class ReasonForIssue(str, PyEnum):
    NEW_BUSINESS = "New Business"
    RENEWAL      = "Renewal"
    MTA          = "MTA"


# ─────────────────────────────────────────────
# TENANTS
# ─────────────────────────────────────────────

class Tenant(Base):
    __tablename__ = "tenants"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name        = Column(String(255), nullable=False)
    email       = Column(String(255), unique=True, nullable=False)
    phone       = Column(String(50), nullable=True)
    company     = Column(String(255), nullable=True)

    username      = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    plan        = Column(Enum(TenantPlan), default=TenantPlan.BASIC, nullable=False)
    status      = Column(Enum(TenantStatus), default=TenantStatus.PENDING, nullable=False)

    expires_at  = Column(DateTime(timezone=True), nullable=True)
    monthly_fee = Column(Numeric(10, 2), default=0.00, nullable=False)

    logo_url    = Column(String(500), nullable=True)
    brand_color = Column(String(7), nullable=True)

    stripe_customer_id = Column(String(255), nullable=True)

    # Date the "policies expiring soon" digest was last emailed to the agent
    expiry_digest_sent_on = Column(Date, nullable=True)

    created_by  = Column(UUID(as_uuid=True), nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    policies    = relationship("Policy", back_populates="tenant")
    drivers     = relationship("Driver", back_populates="tenant")
    vehicles    = relationship("Vehicle", back_populates="tenant")
    billing     = relationship("TenantBilling", back_populates="tenant")

    def __repr__(self):
        return f"<Tenant {self.username} ({self.status})>"


# ─────────────────────────────────────────────
# SUPER ADMIN
# ─────────────────────────────────────────────

class SuperAdmin(Base):
    __tablename__ = "super_admins"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email         = Column(String(255), unique=True, nullable=False)
    username      = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name     = Column(String(255), nullable=False)
    is_active     = Column(Boolean, default=True)

    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<SuperAdmin {self.username}>"


# ─────────────────────────────────────────────
# DRIVERS
# ─────────────────────────────────────────────

class Driver(Base):
    __tablename__ = "drivers"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id      = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)

    first_name     = Column(String(100), nullable=False)
    last_name      = Column(String(100), nullable=False)
    date_of_birth  = Column(Date, nullable=False)          # ← DateTime → Date
    driving_licence = Column(String(100), nullable=False)
    mobile         = Column(String(50), nullable=False)
    email          = Column(String(255), nullable=False)

    address_line_1 = Column(String(255), nullable=False)
    address_line_2 = Column(String(255), nullable=True)
    city           = Column(String(100), nullable=False)
    postcode       = Column(String(20), nullable=False)
    occupation     = Column(String(150), nullable=False)

    is_saved       = Column(Boolean, default=True)

    created_at     = Column(DateTime(timezone=True), server_default=func.now())
    updated_at     = Column(DateTime(timezone=True), onupdate=func.now())

    tenant         = relationship("Tenant", back_populates="drivers")
    policies       = relationship("Policy", back_populates="driver")

    def __repr__(self):
        return f"<Driver {self.first_name} {self.last_name}>"


# ─────────────────────────────────────────────
# VEHICLES
# ─────────────────────────────────────────────

class Vehicle(Base):
    __tablename__ = "vehicles"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id       = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)

    registration    = Column(String(20), nullable=False)
    make            = Column(String(100), nullable=False)
    model           = Column(String(100), nullable=False)
    year            = Column(Integer, nullable=False)
    color           = Column(String(50), nullable=True)

    value_range     = Column(Enum(VehicleValueRange), nullable=False)

    is_saved        = Column(Boolean, default=True)

    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    tenant          = relationship("Tenant", back_populates="vehicles")
    policies        = relationship("Policy", back_populates="vehicle")

    def __repr__(self):
        return f"<Vehicle {self.registration} - {self.make} {self.model}>"


# ─────────────────────────────────────────────
# POLICIES
# ─────────────────────────────────────────────

class Policy(Base):
    __tablename__ = "policies"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id       = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    driver_id       = Column(UUID(as_uuid=True), ForeignKey("drivers.id"), nullable=False)
    vehicle_id      = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)

    policy_number   = Column(String(50), unique=True, nullable=False)

    start_datetime  = Column(DateTime(timezone=True), nullable=False)
    end_datetime    = Column(DateTime(timezone=True), nullable=False)
    price           = Column(Numeric(10, 2), nullable=False)

    cover_type      = Column(Enum(CoverType), default=CoverType.FULLY_COMPREHENSIVE)
    reason_for_issue = Column(Enum(ReasonForIssue), default=ReasonForIssue.NEW_BUSINESS)

    compulsory_excess = Column(Numeric(10, 2), default=500.00)
    voluntary_excess  = Column(Numeric(10, 2), default=0.00)

    status          = Column(Enum(PolicyStatus), default=PolicyStatus.PENDING)

    # Lifecycle
    version                 = Column(Integer, default=1, server_default="1", nullable=False)  # bumped on mid-term adjustments
    cancelled_at            = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason     = Column(String(255), nullable=True)
    expiry_reminder_sent_at = Column(DateTime(timezone=True), nullable=True)

    pdf_certificate_url    = Column(String(500), nullable=True)
    pdf_schedule_url       = Column(String(500), nullable=True)

    email_sent      = Column(Boolean, default=False)
    email_sent_at   = Column(DateTime(timezone=True), nullable=True)

    verify_token    = Column(String(255), nullable=True, unique=True)
    verified_at     = Column(DateTime(timezone=True), nullable=True)

    stripe_payment_intent_id = Column(String(255), nullable=True)

    issued_at       = Column(DateTime(timezone=True), server_default=func.now())
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())

    tenant          = relationship("Tenant", back_populates="policies")
    driver          = relationship("Driver", back_populates="policies")
    vehicle         = relationship("Vehicle", back_populates="policies")
    payment         = relationship("Payment", back_populates="policy", uselist=False)

    def __repr__(self):
        return f"<Policy {self.policy_number} ({self.status})>"


# ─────────────────────────────────────────────
# STATIC DOCUMENTS
# ─────────────────────────────────────────────

class StaticDocument(Base):
    __tablename__ = "static_documents"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name        = Column(String(100), nullable=False)
    url         = Column(String(500), nullable=False)
    version     = Column(String(50), nullable=True)
    is_active   = Column(Boolean, default=True)

    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<StaticDocument {self.name}>"


# ─────────────────────────────────────────────
# PAYMENTS
# ─────────────────────────────────────────────

class Payment(Base):
    __tablename__ = "payments"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_id   = Column(UUID(as_uuid=True), ForeignKey("policies.id"), nullable=False)

    amount      = Column(Numeric(10, 2), nullable=False)
    currency    = Column(String(3), default="GBP")
    status      = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)

    stripe_payment_intent_id = Column(String(255), nullable=True)
    stripe_charge_id         = Column(String(255), nullable=True)

    paid_at     = Column(DateTime(timezone=True), nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    policy      = relationship("Policy", back_populates="payment")

    def __repr__(self):
        return f"<Payment {self.amount} GBP ({self.status})>"


# ─────────────────────────────────────────────
# TENANT BILLING
# ─────────────────────────────────────────────

class TenantBilling(Base):
    __tablename__ = "tenant_billing"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id    = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)

    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end   = Column(DateTime(timezone=True), nullable=False)
    amount       = Column(Numeric(10, 2), nullable=False)
    status       = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)

    stripe_invoice_id = Column(String(255), nullable=True)

    paid_at      = Column(DateTime(timezone=True), nullable=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    tenant       = relationship("Tenant", back_populates="billing")

    def __repr__(self):
        return f"<TenantBilling {self.tenant_id} {self.amount} ({self.status})>"