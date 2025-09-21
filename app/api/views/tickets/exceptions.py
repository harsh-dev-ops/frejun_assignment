from fastapi import status, HTTPException
from typing import Any, Dict


class NoTicketsAvailable(HTTPException):
    def __init__(
        self, 
        status_code: int = status.HTTP_204_NO_CONTENT, 
        detail: Any = "No Tickets available", 
        headers: Dict[str, str] | None = None
        ) -> None:
        super().__init__(
            status_code,
            detail,
            headers
        )