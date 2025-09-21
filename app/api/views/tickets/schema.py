from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.database.models.tickets import GenderEnum, BerthTypeEnum, TicketStatusEnum


class PassengerBase(BaseModel):
    name: str
    age: int
    gender: GenderEnum


class CreatePassenger(PassengerBase):
    pass


class PassengerOut(PassengerBase):
    id: int
    needs_berth: bool
    berth_number: Optional[str] = None
    berth_type: Optional[BerthTypeEnum] = None
    coach: Optional[str] = None

    class Config:
        orm_mode = True


class BerthBase(BaseModel):
    berth_number: str
    type: BerthTypeEnum
    coach: str
    is_available: bool


class BerthOut(BerthBase):
    id: int
    train_id: int

    class Config:
        orm_mode = True


class TicketBase(BaseModel):
    pnr: str
    status: TicketStatusEnum


class CreateTicket(TicketBase):
    train_id: int


class TicketOut(TicketBase):
    id: int
    created_at: datetime
    train_id: int
    passengers: List[PassengerOut]

    class Config:
        orm_mode = True


class CreateBooking(BaseModel):
    passengers: List[CreatePassenger]
    train_id: int


class CancelOut(BaseModel):
    message: str


class BookedTicketsOut(BaseModel):
    tickets: List[TicketOut]
    count: int


class AvailableTicketsOut(BaseModel):
    available: dict
    total: dict
    available_berths: List[BerthOut]