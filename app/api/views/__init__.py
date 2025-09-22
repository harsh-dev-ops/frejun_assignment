from fastapi import APIRouter
from app.api.views.health_check.routers import router as health_check_router
from app.api.views.tickets.routers import router as ticket_router
from app.api.views.trains.routers import router as train_router


api_router = APIRouter()

api_router.include_router(
    router=train_router,
    prefix='/v1/trains',
    tags=['Trains']
)


api_router.include_router(
    router = ticket_router,
    prefix='/v1/tickets',
    tags=['Tickets']
)


api_router.include_router(
    router=health_check_router,
    prefix='',
    tags=['Healthcheck']
)
