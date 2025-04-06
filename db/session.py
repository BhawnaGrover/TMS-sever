from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.base import Base
from models.user import User
from models.task import Task

DATABASE_URL = "sqlite:///./hello.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread":False}) #check_same_thread=False allows the use of the same connection in different threads.

SessionLocal = sessionmaker(autocommit=False, autoflush=False,bind=engine)

Base.metadata.create_all(bind=engine) #this command creates the table in the database based on models we have defined

def get_db():
    db = SessionLocal()
    try:
        yield db  #yield in python is used to return a value and pause the function. In the context of fast API, this allows the session to be used in the API endpoint after the endpoint completes control returns to get_db() and finally db.close() ensures that the database session is closed after the request is processed  
    finally:
        db.close()