import sqlalchemy as sa
from sqlalchemy.orm import Session
from .crud_mixins import BaseCrudMixin
    

class BaseCrud(BaseCrudMixin):
    def __init__(self, session: Session, Model):
        self.session = session
        self.Model = Model
        
    def get_all(self, page=0, page_size=10):
        query = self.session.query(self.Model).filter().order_by(
            sa.desc(self.Model.updated_at))
        return self.pagination(query, page, page_size)
    
    def create(self, data):
        try:
            obj = self.Model(**data)
            self.session.add(obj)
            self.session.commit()
            return obj
        except Exception:
            self.session.rollback()
        
    def create_many(self, data_list):
        obj_list = [self.Model(**data) for data in data_list]
        obj = self.session.add_all(obj_list)
        self.session.commit()
        return obj
    
    def get(self, _id):
        obj = self.session.query(self.Model).filter(self.Model.id == _id).first()
        self.missing_obj(obj, _id)
        return obj
    
    def update(self, _id:int, data:dict):
        obj = self.session.query(self.Model).filter(self.Model.id == _id).first()
        self.missing_obj(obj, _id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            self.session.commit()
            self.session.refresh(obj)
        return obj
    
    def delete(self, _id):
        obj = self.session.query(self.Model).filter(self.Model.id == _id).first()
        self.missing_obj(obj, _id)
        if obj:
            self.session.delete(obj)
            self.session.commit()

