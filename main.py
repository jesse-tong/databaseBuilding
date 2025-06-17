from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
import os, dotenv, json

from app.upload_cv import router as upload_cv_router
from settings import get_settings
from schema.InitDB import createDBAndTables, getSession, engine
from modules.read_cv_directory.CVProcessor import CVProcessor
from modules.parse_cv.ParseCVFiles import parseCVs
from database.VectorDB import vector_store
from controller.ProcessCVController import ProcessCVController
from routes.CVUploadRoutes import router as cv_upload_router

dotenv.load_dotenv(dotenv.find_dotenv())

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    createDBAndTables()
    yield
    # Cleanup code can be added here if needed

app = FastAPI(lifespan=lifespan)
app.include_router(upload_cv_router, prefix="/upload", tags=["upload"])
# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "default_secret_key"))
app.include_router(cv_upload_router, prefix="/cv", tags=["cv"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

