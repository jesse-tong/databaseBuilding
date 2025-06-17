from langchain.vectorstores import VectorStore
from langchain_core.documents import Document
from langchain_community.vectorstores.utils import filter_complex_metadata

from database.BaseQuery import BaseQueryObject
from typing import List, Any, Optional, TypeVar, Type

class VectorQueryObject(BaseQueryObject):
    def __init__(self, schema_class: Type[Document], engine: VectorStore):
        super().__init__(schema_class, engine)

    def add(self, obj: Document, **kwargs) -> Document:
        id = kwargs.get("id", None)
        # We need to ensure that the metadata is filtered to avoid None and non-primitive types
        # since vector databases only support primitive types in metadata.
        obj = filter_complex_metadata([obj])[0]
        obj.metadata = dict() if obj.metadata is None else obj.metadata
        self.engine.add_documents(documents=[obj], ids=[id] if id else None)
        return obj

    def update(self, id_: Any, new_data: Document) -> Optional[Document]:
        # Delete the old document and add the new one
        self.engine.delete([id_])
        new_data = filter_complex_metadata([new_data])[0]
        new_data.metadata = dict() if new_data.metadata is None else new_data.metadata 
        new_data.id = id_ 
        self.engine.add_documents(documents=[new_data], ids=[id_])
        new_data.id = id_
        return new_data

    def delete(self, id_: Any) -> Optional[Document]:
        self.engine.delete([id_])
        return None

    def select(self, **kwargs) -> List[Document]:
        return self.engine.similarity_search(kwargs.get("query", ""), k=kwargs.get("k", 10))
    
    def selectByIds(self, ids: List[Any]) -> List[Document]:
        try:
            docs = self.engine.get_by_ids(ids)
        except Exception as e:
            raw = self.engine._collection.get(ids=ids, include=["documents", "metadatas"])

            # Patch metadata=None to metadata={}
            docs = []
            for content, metadata in zip(raw["documents"], raw["metadatas"]):
                docs.append(Document(
                    page_content=content,
                    metadata=metadata if metadata is not None else {}
                ))
        return filter_complex_metadata(docs) if ids else []
    

    def selectIn(self, attr: str, values: List[Any]) -> List[Document]:
        retrievedDocs = []
        for value in values:
            retrievedDocs.extend(self.engine.similarity_search(
                query=value, k=10))
        return retrievedDocs
        
    def selectLike(self, attr: str, value: str) -> List[Document]:
        # Vector stores typically do not support direct filtering; this is a placeholder
        return []