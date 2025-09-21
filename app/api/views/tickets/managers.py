from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import Session
from app.api.views.tickets.data_types import CapacityCounts
from app.api.views.tickets.helpers import TrainHelper
from app.api.views.tickets.schema import CreateBooking, CreatePassenger, CreateTicket, TicketStatusEnum
from app.database.crud.tickets import BerthCrud, PassengerCrud, TicketCrud, TrainCrud
from app.database.models.tickets import BerthTypeEnum, GenderEnum

class _TicketManager(ABC):
    @abstractmethod
    async def get_capacity_counts(self, train_id: int):
        pass
    
    @abstractmethod
    async def assign_berth(self, train_id: int, passenger: CreatePassenger, status: TicketStatusEnum):
        pass
    
    @abstractmethod
    async def promote_rac_to_confirmed(self, train_id: int):
        pass
    

class TicketManager(_TicketManager):
    def __init__(self, session: Session) -> None:
        self.train_crud = TrainCrud(session)
        self.ticket_crud = TicketCrud(session)
        self.berth_crud = BerthCrud(session)
        self.passenger_crud = PassengerCrud(session)
        self.train_helper = TrainHelper()
        self.session = session
    
    async def get_capacity_counts(self, train_id: int):
        
        train = self.train_crud.get_train(train_id)
        ticket_counts = self.ticket_crud.get_ticket_count_by_status(train_id)
        
        confirmed_count = ticket_counts.get(TicketStatusEnum.CONFIRMED, 0)
        rac_count = ticket_counts.get(TicketStatusEnum.RAC, 0)
        waiting_count = ticket_counts.get(TicketStatusEnum.WAITING_LIST, 0)
        
        return CapacityCounts(
            total_confirmed = train.total_confirmed_berths,
            total_rac = train.total_rac_berths * 2,
            total_waiting = train.total_waiting_list,
            available_confirmed= max(0, train.total_confirmed_berths - confirmed_count),
            available_rac= max(0, (train.total_rac_berths * 2) - rac_count),
            available_waiting= max(0, train.total_waiting_list - waiting_count)
        )
    
    async def assign_berth(self, train_id: int, passenger: CreatePassenger, status: TicketStatusEnum):
        
        if (status == TicketStatusEnum.CONFIRMED and 
            (passenger.age >= 60 or (
                passenger.gender == GenderEnum.FEMALE and passenger.age < 5))):
            
            available_berths = self.berth_crud.get_available_berths(train_id, BerthTypeEnum.LOWER)
            if available_berths:
                return available_berths[0]
        
        if status == TicketStatusEnum.RAC:
            available_berths = self.berth_crud.get_available_berths(train_id, BerthTypeEnum.SIDE_LOWER)
            if available_berths:
                return available_berths[0]
        
        available_berths = self.berth_crud.get_available_berths(train_id)
        return available_berths[0] if available_berths else None
    
    async def promote_rac_to_confirmed(self, train_id: int):
        rac_tickets = self.ticket_crud.get_tickets_by_status(train_id, TicketStatusEnum.RAC)

        if not rac_tickets:
            return None
        
        available_berths = self.berth_crud.get_available_berths(train_id)
        if not available_berths:
            return None

        rac_ticket = rac_tickets[0]
        self.ticket_crud.update_ticket_status(rac_ticket.id, TicketStatusEnum.CONFIRMED)

        for passenger in rac_ticket.passengers:
            if passenger.needs_berth and not passenger.berth_id:
                passenger_payload = CreatePassenger(
                    name=passenger.name,
                    age=passenger.age,
                    gender=passenger.gender
                )
                berth = await self.assign_berth(train_id, passenger_payload, TicketStatusEnum.CONFIRMED)
                
                if berth:
                    passenger.berth_id = berth.id
                    self.berth_crud.update_berth_availability(berth.id, False)
        
        self.session.commit()
    
    async def promote_waiting_to_rac(self, train_id: int):
        waiting_tickets = self.ticket_crud.get_tickets_by_status(train_id, TicketStatusEnum.WAITING_LIST)
        
        if not waiting_tickets:
            return None
        
        available_rac_berths = self.berth_crud.get_available_berths(train_id, BerthTypeEnum.SIDE_LOWER)
        if not available_rac_berths:
            return None
        
        waiting_ticket = waiting_tickets[0]
        self.ticket_crud.update_ticket_status(waiting_ticket.id, TicketStatusEnum.RAC)
        
        for passenger in waiting_ticket.passengers:
            if passenger.needs_berth and not passenger.berth_id:
                passenger_payload = CreatePassenger(
                    name=passenger.name,
                    age=passenger.age,
                    gender=passenger.gender
                )
                berth = await self.assign_berth(train_id, passenger_payload, TicketStatusEnum.RAC)
                
                if berth:
                    passenger.berth_id = berth.id
                    self.berth_crud.update_berth_availability(berth.id, False)
        
        self.session.commit()