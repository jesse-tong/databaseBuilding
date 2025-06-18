from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
import os, dotenv, json

from settings import get_settings
from schema.InitDB import createDBAndTables, getSession, engine
from modules.read_cv_directory.CVProcessor import CVProcessor
from modules.parse_cv.ParseCVFiles import parseCVs
from database.VectorDB import vector_store
from controller.ProcessCVController import ProcessCVController
from routes.CVUploadRoutes import router as cv_upload_router
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

dotenv.load_dotenv(dotenv.find_dotenv())

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    createDBAndTables()
    yield
    # Cleanup code can be added here if needed

app = FastAPI(lifespan=lifespan)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    errors = exc.errors()
    error_messages = [{ 'errorAt': error['loc'][0], 'attribute': error['loc'][-1], 'errorMessage': error['msg'] } for error in errors]
    return JSONResponse(
        status_code=422,
        content={ 'message': 'Invalid data in request.', 'errors': error_messages }
    )

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "default_secret_key"))
app.include_router(cv_upload_router, tags=["cv"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

