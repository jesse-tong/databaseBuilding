from sqlmodel import Session, select
from typing import List, Any
from database.BaseQuery import BaseQueryObject
from schema.Application import Application

class SqlQueryObject(BaseQueryObject):
    def __init__(self, schema_class, engine):
        super().__init__(schema_class, engine)

    def add(self, obj: Any, **kwargs):
        with Session(self.engine) as session:
            session.add(obj)
            session.commit()
            session.refresh(obj)
        return obj
    
    def update(self, id_: Any, new_data: dict):
        with Session(self.engine) as session:
            obj = session.get(self.schema_class, id_)
            if not obj:
                return None
            for key, value in new_data.items():
                setattr(obj, key, value)
            session.commit()
            session.refresh(obj)
        return obj
    
    def updateWithObject(self, id_: Any, new_data: Any):
        with Session(self.engine) as session:
            obj = session.get(self.schema_class, id_)
            oldObjId = obj.id if obj else None
            if not obj:
                return None
            new_data.id = oldObjId
            # Upsert, updates if exists, inserts if not, but in this case it updates as there is an object with the same ID
            session.merge(new_data) 
            session.commit()
            session.refresh(obj)
        return obj
    
    def delete(self, id_: Any):
        with Session(self.engine) as session:
            obj = session.get(self.schema_class, id_)
            if not obj:
                return None
            session.delete(obj)
            session.commit()
        return obj
    
    def select(self, **kwargs) -> List[Any]:
        with Session(self.engine) as session:
            query = select(self.schema_class)
            for key, value in kwargs.items():
                query = query.where(getattr(self.schema_class, key) == value)
            results = session.exec(query).all()
        return results
    
    def selectIn(self, attr: str, values: List[Any]) -> List[Any]:
        with Session(self.engine) as session:
            query = select(self.schema_class).where(getattr(self.schema_class, attr).in_(values))
            results = session.exec(query).all()
        return results
    
    def selectLike(self, attr: str, value: str) -> List[Any]:
        with Session(self.engine) as session:
            query = select(self.schema_class).where(getattr(self.schema_class, attr).ilike(f"%{value}%"))
            results = session.exec(query).all()
        return results

    