from enum import Enum
from typing import List
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.database.crud.base import BaseCrud
from app.database.models.tickets import BerthModel, PassengerModel, TicketModel, TrainModel, GenderEnum, TicketStatusEnum, BerthTypeEnum
from abc import ABC, abstractmethod


class _TrainCrud(ABC):
    @abstractmethod
    def get_train(self, train_id: int) -> TrainModel | None:
        pass
    

class _BerthCrud(ABC):
    @abstractmethod
    def get_berth(self, berth_id: int) -> BerthModel | None:
        pass
    
    @abstractmethod
    def get_available_berths(self, train_id: int, berth_type: BerthTypeEnum | None = None):
        pass
    
    @abstractmethod
    def update_berth_availability(self, berth_id: int, is_available: bool):
        pass


class _TicketCrud(ABC):
    @abstractmethod
    def get_ticket(self, ticket_id: int) -> TicketModel | None:
        pass
    
    @abstractmethod
    def get_tickets(self, train_id: int, page: int = 1 , page_size: int = 20):
        pass
    
    @abstractmethod
    def update_ticket_status(self, ticket_id: int, status: TicketStatusEnum):
        pass
    
    @abstractmethod
    def get_ticket_count_by_status(self, train_id: int):
        pass
    
    @abstractmethod
    def get_tickets_by_status(self, train_id: int, status: TicketStatusEnum):
        pass
    
    @abstractmethod
    def create_ticket(self, data:dict):
        pass
    

class _PassengerCrud(ABC):
    @abstractmethod
    def create_passenger(self, passenger_data: dict, ticket_id: int, berth_id: int | None = None):
        pass


class TrainCrud(BaseCrud, _TrainCrud):
    def __init__(self, session: Session, Model = TrainModel):
        super().__init__(session, Model)
    
    def get_train(self, train_id: int) -> TrainModel | None:
        stmt = sa.select(TrainModel).where(
            TrainModel.id == train_id
        )
        train = self.session.execute(stmt).scalar_one_or_none()
        self.missing_obj(train, detail = f"Train with ID: {train_id} not found!")
        return train
        

class BerthCrud(BaseCrud, _BerthCrud):
    def __init__(self, session: Session, Model = BerthModel):
        super().__init__(session, Model)
        
    def get_berth(self, berth_id: int) -> BerthModel | None:
        return super().get(berth_id)
    
    def get_available_berths(self, train_id: int, berth_type: BerthTypeEnum | None = None):
        stmt = sa.select(
            BerthModel
        ).where(
            BerthModel.train_id == train_id,
            BerthModel.is_available == True
        )
        
        if berth_type:
            stmt.where(BerthModel.type == berth_type)
        
        berths = self.session.execute(stmt).scalars().all()
        return berths
    
    def update_berth_availability(self, berth_id: int, is_available: bool):
        try:
            stmt = sa.update(
            BerthModel
            ).where(
                BerthModel.id == berth_id,
            ).values(
                is_available = is_available
            ).returning(
                BerthModel
            )
            ticket = self.session.execute(stmt).scalar_one()
            self.session.commit()
            return ticket
        except Exception:
            self.session.rollback()
        
    
class TicketCrud(BaseCrud, _TicketCrud):
    def __init__(self, session: Session, Model = TicketModel):
        super().__init__(session, Model)
        
    def get_ticket(self, ticket_id: int) -> TicketModel | None:
        return super().get(ticket_id)
    
    def get_tickets(self, train_id: int, only_booked_tickets: bool = True, page: int = 1, page_size: int = 20):
        
        stmt = sa.select(
            TicketModel
        ).where(
            TicketModel.train_id == train_id,
        )
        
        if only_booked_tickets:
            stmt.where(TicketModel.status != TicketStatusEnum.CANCELLED)
        
        stmt = self.pagination_query(stmt, page, page_size)
        tickets = self.session.execute(stmt).scalars().all()
        
        return tickets

    def get_ticket_count_by_status(self, train_id: int):
        stmt = sa.select(
            TicketModel.status,
            sa.func.count(TicketModel.id)
        ).where(
            TicketModel.train_id == train_id,
            TicketModel.status != TicketStatusEnum.CANCELLED
        ).group_by(
            TicketModel.status
        )
        result = self.session.execute(stmt).all()
        return {status: count for status, count in result}
    
    def get_tickets_by_status(self, train_id: int, status: TicketStatusEnum):
        stmt = sa.select(TicketModel).where(
            TicketModel.train_id == train_id,
            TicketModel.status == status
        ).order_by(
            TicketModel.created_at
        )
        tickets = self.session.execute(stmt).scalars().all()
        return tickets
        
    def update_ticket_status(self, ticket_id: int, status: TicketStatusEnum):
        try:
            stmt = sa.update(
            TicketModel
            ).where(
                TicketModel.id == ticket_id,
            ).values(
                status=status
            ).returning(
                TicketModel
            )
            ticket = self.session.execute(stmt).scalar_one()
            self.session.commit()
            return ticket
        except Exception:
            self.session.rollback()
            
    def create_ticket(self, data: dict) -> TicketModel | None:
        return super().create(data)
    
            
class PassengerCrud(BaseCrud, _PassengerCrud):
    def __init__(self, session: Session, Model = PassengerModel):
        super().__init__(session, Model)
    
    def create_passenger(self, passenger_data: dict, ticket_id: int, berth_id: int | None = None):
        
        passenger_data['ticket_id'] = ticket_id
        passenger_data['berth_id'] = berth_id
        passenger_data['needs_berth'] = passenger_data['age'] >= 5
        
        return super().create(passenger_data)
        
