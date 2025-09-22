from typing import List
from fastapi import APIRouter, status
from app.api.views.trains.schemas import CreateTrain, TrainOut, AllTrainOut
from app.api.views.trains.services import TrainService
from app.database.deps import db_dependency


router = APIRouter()

@router.get('', status_code=status.HTTP_200_OK, response_model=List[AllTrainOut])
async def get_trains(
    session: db_dependency, 
    page: int = 1, 
    page_size: int = 10
    ):
    
    service = TrainService(session)
    return await service.get_trains(page, page_size)


@router.get('/{train_id}', status_code=status.HTTP_200_OK, response_model=TrainOut)
async def get_train(
    session: db_dependency, 
    train_id: int
    ):
    
    service = TrainService(session)
    return await service.get_train(train_id)


@router.post('', status_code=status.HTTP_201_CREATED, response_model=TrainOut)
async def create_train(
    session: db_dependency, 
    payload: CreateTrain
    ):
    
    service = TrainService(session)
    return await service.create_train(payload)


@router.delete('/{train_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_train(
    session: db_dependency, 
    train_id: int
    ):
    service = TrainService(session)
    return await service.delete_train(train_id)

