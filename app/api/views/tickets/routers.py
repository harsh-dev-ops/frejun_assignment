from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.views.tickets.schema import AvailableTicketsOut, BookedTicketsOut, CancelOut, CreateBooking, TicketOut
from app.api.views.tickets.services import TicketService
from app.database.deps import db_dependency


router = APIRouter()

@router.get('/booked', status_code=status.HTTP_200_OK, response_model=BookedTicketsOut)
async def get_booked_tickects(
    session: db_dependency, 
    train_id: int, 
    page: int = 1, 
    page_size: int = 20
    ):
    
    service = TicketService(session)
    return await service.get_booked_tickets(train_id, page, page_size)


@router.get('/available', status_code=status.HTTP_200_OK, response_model=AvailableTicketsOut)
async def get_available_tickects(
    session: db_dependency, 
    train_id: int, 
    ):
    
    service = TicketService(session)
    return await service.get_available_tickets(train_id)


@router.post('/book', status_code=status.HTTP_201_CREATED, response_model=TicketOut)
async def book_ticket(
    session: db_dependency,
    payload: CreateBooking
):
    
    service = TicketService(session)
    return await service.book_ticket(payload)


@router.patch('/cancel/{ticket_id}', status_code=status.HTTP_202_ACCEPTED, response_model=CancelOut)
async def cancel_booking(
    session: db_dependency,
    ticket_id: int
):
    
    service = TicketService(session)
    await service.cancel_ticket(ticket_id)
    return {"message": "Ticket cancelled successfully"}
