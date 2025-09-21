from fastapi import HTTPException
import sqlalchemy as sa

class BaseCrudMixin:
    def missing_obj(
        self, 
        obj, 
        _id:int | str | None = None,
        detail: str = ""
        ):
        
        if obj is None:
            detail = "Object with ID: {_id} not found!" if not detail else detail
            raise HTTPException(detail=detail.format(_id=_id), status_code=404)
        
    def pagination(self, query, page:int = 0, page_size:int = 10):
        if page_size:
            query = query.limit(page_size)
        if page:
            query = query.offset(page*page_size)
        return query.all()

    def pagination_query(self, stmt: sa.Select, page: int = 1, page_size: int = 20):
        if page_size:
            stmt = stmt.limit(page_size)
        if page - 1:
            stmt = stmt.offset((page - 1)  * page_size)
        return stmt
            
            