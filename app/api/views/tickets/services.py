from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.api.views.tickets.exceptions import NoTicketsAvailable
from app.api.views.tickets.helpers import TrainHelper
from app.api.views.tickets.managers import TicketManager
from app.api.views.tickets.schema import CreateBooking, TicketStatusEnum
from app.database.crud.tickets import BerthCrud, PassengerCrud, TicketCrud, TrainCrud


class _TicketService(ABC):
    @abstractmethod
    async def book_ticket(self, payload: CreateBooking):
        pass
    
    @abstractmethod
    async def cancel_ticket(self, ticket_id: int):
        pass
    
    @abstractmethod
    async def get_booked_tickets(self, train_id: int, page: int, page_size: int):
        pass
    
    @abstractmethod
    async def get_available_tickets(self, train_id: int):
        pass
    

class TicketService(_TicketService):
    def __init__(self, session: Session) -> None:
        self.train_crud = TrainCrud(session)
        self.ticket_crud = TicketCrud(session)
        self.berth_crud = BerthCrud(session)
        self.passenger_crud = PassengerCrud(session)
        self.train_helper = TrainHelper()
        self.manager = TicketManager(session)
        self.session = session
    
    async def get_booked_tickets(self, train_id: int, page: int, page_size: int):
        return self.ticket_crud.get_tickets(train_id, True, page, page_size)
    
    async def get_available_tickets(self, train_id: int):
        capacity = await self.manager.get_capacity_counts(train_id)
        available_berths = self.berth_crud.get_available_berths(train_id)
        return {
            "available": {
                "confirmed": capacity.available_confirmed,
                "rac": capacity.available_rac,
                "waiting_list": capacity.available_waiting
            },
            "total": {
                "confirmed": capacity.total_confirmed,
                "rac": capacity.total_rac,
                "waiting_list": capacity.total_waiting
            },
            "available_berths": available_berths
        }
    
    async def book_ticket(self, payload: CreateBooking):
        try:
            capacity = await self.manager.get_capacity_counts(payload.train_id)
            
            passengers_needing_berth = [p for p in payload.passengers if p.age >= 5]
            needed_berths = len(passengers_needing_berth)
            
            if needed_berths <= capacity.available_confirmed:
                status = TicketStatusEnum.CONFIRMED
            elif needed_berths <= capacity.available_confirmed + capacity.available_rac:
                status = TicketStatusEnum.RAC
            elif needed_berths <= capacity.available_confirmed + capacity.available_rac + capacity.available_waiting:
                status = TicketStatusEnum.WAITING_LIST
            else:
                raise NoTicketsAvailable()

            ticket = self.ticket_crud.create_ticket({
                'pnr': self.train_helper.generate_pnr(),
                'status': status,
                'train_id': payload.train_id
            })
            
            for passenger in payload.passengers:
                berth = None
                if passenger.age >= 5 and status in [TicketStatusEnum.CONFIRMED, TicketStatusEnum.RAC]:
                    berth = await self.manager.assign_berth(payload.train_id, passenger, status)
                    if berth:
                        self.berth_crud.update_berth_availability(berth.id, False)
                
                self.passenger_crud.create_passenger(passenger.model_dump(exclude_none=True), ticket.id, berth.id if berth else None)
            
            self.session.refresh(ticket)
            return ticket
        except SQLAlchemyError as e:
            print(e)
            self.session.rollback()
            raise e
    
    async def cancel_ticket(self, ticket_id: int):
        try:
            ticket = self.ticket_crud.get_ticket(ticket_id)
            
            if ticket.status == TicketStatusEnum.CANCELLED:
                return  None
            
            for passenger in ticket.passengers:
                if passenger.berth_id:
                    self.berth_crud.update_berth_availability(passenger.berth_id, True)
            
            self.ticket_crud.update_ticket_status(ticket_id, TicketStatusEnum.CANCELLED)
            
            if ticket.status == TicketStatusEnum.CONFIRMED:
                await self.manager.promote_rac_to_confirmed(ticket.train_id)
                await self.manager.promote_waiting_to_rac(ticket.train_id)
            elif ticket.status == TicketStatusEnum.RAC:
                await self.manager.promote_waiting_to_rac(ticket.train_id)
                
        except SQLAlchemyError as e:
            print(e)
            self.session.rollback()
            raise e
        