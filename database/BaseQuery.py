from sqlmodel import SQLModel, select
from typing import Annotated, List, Optional, Type, TypeVar, Any, Union, Dict
from abc import ABC, abstractmethod

from langchain_core.documents import Document
from langchain_chroma.vectorstores import VectorStore

SchemaType = TypeVar("SchemaType", bound=Union[SQLModel, Document])

class BaseQueryObject(ABC):
    def __init__(self, schema_class: Type[SchemaType], engine: Any):
        self.schema_class = schema_class
        self.query = select(schema_class) if issubclass(schema_class, SQLModel) else None
        self.engine = engine

    @abstractmethod
    def add(self, obj: SchemaType, **kwargs):
        pass

    @abstractmethod
    def update(self, id_: Any, new_data: Union[Dict[str, Any], SchemaType, Document]):
        pass

    @abstractmethod
    def delete(self, id_: Any):
        pass

    @abstractmethod
    def select(self, **kwargs):
        pass

    @abstractmethod
    def selectIn(self, attr: str, values: List[Any]):
        pass

    @abstractmethod
    def selectLike(self, attr: str, value: str):
        pass


    
