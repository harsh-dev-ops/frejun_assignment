from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.api.views.trains.schemas import TrainOut
from app.database.models.tickets import GenderEnum, BerthTypeEnum, TicketStatusEnum


class PassengerBase(BaseModel):
    name: str
    age: int
    gender: GenderEnum


class CreatePassenger(PassengerBase):
    pass





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


class PassengerOut(PassengerBase):
    id: int
    needs_berth: bool
    berth: BerthOut | None = None

    class Config:
        orm_mode = True
        

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
    count: int = 0


class AvailableTicketsOut(BaseModel):
    available: dict
    total: dict
    available_berths: List[BerthOut]