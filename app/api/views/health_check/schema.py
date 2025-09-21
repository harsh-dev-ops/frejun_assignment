from pydantic import BaseModel


class HealthStatusResponse(BaseModel):
    status: str = "OK"
    healthy: bool = True
    message: str = "Server is running"
    