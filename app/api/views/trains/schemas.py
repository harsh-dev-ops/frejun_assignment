from typing import List
from pydantic import BaseModel

from app.database.models.tickets import BerthTypeEnum


class CreateTrain(BaseModel):
    name: str
    total_confirmed_berths: int = 63
    total_rac_berths: int = 9
    total_waiting_list: int = 10


class AllTrainOut(CreateTrain):
    id: int
    
    
class BerthOut(BaseModel):
    id: int
    berth_number: str
    type: BerthTypeEnum
    coach: str
    is_available: bool


class TrainOut(CreateTrain):
    id: int
    berths: List[BerthOut]
    

class UpdateTrain(BaseModel):
    name: str | None
    total_confirmed_berths: int | None
    total_rac_berths: int | None
    total_waiting_list: int | None