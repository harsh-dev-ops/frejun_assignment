from fastapi import APIRouter, Request, status
from app.api.views.health_check.schema import HealthStatusResponse

router = APIRouter()

@router.get("/healthz", 
         status_code=status.HTTP_200_OK,
         response_model=HealthStatusResponse)
async def get_health(request: Request):
    return HealthStatusResponse()

