import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref
from app.database.models.base import Base
from enum import Enum
from typing import List


class BerthTypeEnum(str, Enum):
    LOWER = "lower"
    MIDDLE = "middle"
    UPPER = "upper"
    SIDE_LOWER = "side_lower"

class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class TicketStatusEnum(str, Enum):
    CONFIRMED = "confirmed"
    RAC = "rac"
    WAITING_LIST = "waiting_list"
    CANCELLED = "cancelled"


class TrainModel(Base):
    __tablename__ = "trains"
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    total_confirmed_berths: Mapped[int] = mapped_column(default=63)
    total_rac_berths: Mapped[int] = mapped_column(default=9)
    total_waiting_list: Mapped[int] = mapped_column(default=10)
    
    berths: Mapped[list["BerthModel"]] = relationship(
        "BerthModel", backref=backref("train_berths", cascade="all, delete-orphan"))
    tickets: Mapped[list["TicketModel"]] = relationship(
        "TicketModel", backref=backref("train_tickets", cascade="all, delete-orphan"))


class BerthModel(Base):
    __tablename__ = "berths"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    train_id: Mapped[int] = mapped_column(sa.ForeignKey("trains.id"), nullable=False)
    berth_number: Mapped[str] = mapped_column(sa.String, nullable=False)
    type: Mapped[BerthTypeEnum] = mapped_column(sa.Enum(BerthTypeEnum), nullable=False)
    coach: Mapped[str] = mapped_column(sa.String, nullable=False)
    is_available: Mapped[bool] = mapped_column(default=True)
    
    passengers: Mapped[list["PassengerModel"]] = relationship(
        "PassengerModel", backref=backref("berth_passengers"))


class TicketModel(Base):
    __tablename__ = "tickets"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    pnr: Mapped[str] = mapped_column(sa.String, unique=True, index=True, nullable=False)
    status: Mapped[TicketStatusEnum] = mapped_column(sa.Enum(TicketStatusEnum), nullable=False)
    created_at: Mapped[sa.DateTime] = mapped_column(sa.DateTime(timezone=True), server_default=sa.func.now())
    train_id: Mapped[int] = mapped_column(sa.ForeignKey("trains.id"), nullable=False)
    
    passengers: Mapped[List["PassengerModel"]] = relationship(
        "PassengerModel", backref=backref("ticket_passengers", cascade="all, delete-orphan"))


class PassengerModel(Base):
    __tablename__ = "passengers"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticket_id: Mapped[int] = mapped_column(sa.ForeignKey("tickets.id"), nullable=False)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    gender: Mapped[GenderEnum] = mapped_column(sa.Enum(GenderEnum), nullable=False)
    berth_id: Mapped[int | None] = mapped_column(sa.ForeignKey("berths.id"), nullable=True)
    needs_berth: Mapped[bool] = mapped_column(default=True)
    
    __table_args__ = (
        sa.CheckConstraint('(age >= 5 AND needs_berth = TRUE) OR (age < 5 AND needs_berth = FALSE)', 
                       name='age_berth_constraint'),
    )