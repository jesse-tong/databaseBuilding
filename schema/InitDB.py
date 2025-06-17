from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import Depends
from typing import Annotated
from settings import get_settings
from sqlalchemy_utils import database_exists, create_database

settings = get_settings()
# Create the database engine
engine = create_engine(
    f"mysql+pymysql://{settings.mariadb_username}:{settings.mariadb_password}@{settings.mariadb_host}:{settings.mariadb_port}/{settings.mariadb_database}",
    echo=True
)

def createDBAndTables():
    """
    Create the database and tables if they do not exist.
    """
    #Create the database if it does not exist
    if not database_exists(engine.url):
        create_database(engine.url)
        print(f"Database {settings.mariadb_database} created.")
    SQLModel.metadata.create_all(engine)

def getSession():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(getSession)]



