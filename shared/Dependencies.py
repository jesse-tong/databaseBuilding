from fastapi import Depends
from controller.ProcessCVController import ProcessCVController
from schema.InitDB import engine
from database.VectorDB import vector_store
from settings import get_settings

settings = get_settings()

async def getProcessCVController() -> ProcessCVController:
    """
    Dependency to get an instance of ProcessCVController.
    """
    return ProcessCVController(sqlEngine=engine, vectorStore=vector_store, baseCVStoragePath=settings.default_cv_storage_path)

async def getDatabaseEngine():
    return engine

async def getVectorStore():
    return vector_store