from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from app.api.views.trains.schemas import CreateTrain
from app.database.crud.tickets import TrainCrud


class _TrainService(ABC):
    @abstractmethod
    async def get_trains(self, page: int = 1, page_size: int = 10):
        pass
    
    @abstractmethod
    async def get_train(self, train_id: int):
        pass
    
    @abstractmethod
    async def create_train(self, payload: CreateTrain):
        pass
    
    @abstractmethod
    async def delete_train(self, train_id: int):
        pass
    

class TrainService(_TrainService):
    def __init__(self, session: Session) -> None:
        self.crud = TrainCrud(session)
        self.session = session
    
    async def get_train(self, train_id: int):
        return self.crud.get_train(train_id)
    
    async def get_trains(self, page: int = 1, page_size: int = 10):
        return self.crud.get_trains(page, page_size)
    
    async def create_train(self, payload: CreateTrain):
        return self.crud.create_train(payload.model_dump())
    
    async def delete_train(self, train_id: int):
        return self.crud.delete_train(train_id)