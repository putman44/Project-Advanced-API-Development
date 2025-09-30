import uuid
from datetime import date
from typing import List
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Date, Float, ForeignKey, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

service_mechanics = Table(
    "service_mechanics",
    Base.metadata,
    Column("service_ticket_id", ForeignKey("service_tickets.id", ondelete="CASCADE")),
    Column("mechanic_id", ForeignKey("mechanics.id", ondelete="CASCADE")),
)


def generate_uuid():
    return str(uuid.uuid4())


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_uuid: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, default=generate_uuid
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="customer")
    token_version: Mapped[int] = mapped_column(Integer, default=1)

    service_tickets: Mapped[List["ServiceTicket"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )


class Mechanic(Base):
    __tablename__ = "mechanics"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_uuid: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, default=generate_uuid
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    role: Mapped[str] = mapped_column(String(50), default="mechanic")
    token_version: Mapped[int] = mapped_column(Integer, default=1)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    salary: Mapped[float] = mapped_column(nullable=False)

    service_tickets: Mapped[List["ServiceTicket"]] = relationship(
        secondary=service_mechanics, back_populates="mechanics"
    )


class ServiceTicket(Base):
    __tablename__ = "service_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    VIN: Mapped[str] = mapped_column(String(255), nullable=False)
    service_date: Mapped[date] = mapped_column(Date, nullable=False)
    service_desc: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE")
    )

    customer: Mapped["Customer"] = relationship(back_populates="service_tickets")
    mechanics: Mapped[List["Mechanic"]] = relationship(
        secondary=service_mechanics, back_populates="service_tickets"
    )
