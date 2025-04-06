from fastapi import APIRouter,Depends, HTTPException
from schemas.user_schema import UserCreate, UserResponse, Token , TokenData
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from db.session import get_db 
from models.user import User
from datetime import datetime, timedelta
import jwt
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, OAuth2PasswordRequestForm
import logging

logger = logging.getLogger("uvicorn.error")

security = HTTPBearer()
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256" 

oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="login") #"/login"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
user_router_tms = APIRouter()

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token:str = Depends(oauth_2_scheme), db: Session = Depends(get_db)):
    credential_exception = HTTPException(
        status_code=401, 
        detail="Could not validate credentials", 
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload=jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM])
        username: str=payload.get("sub")
        if username is None:
            raise credential_exception
        
        token_data = TokenData(username=username)

    except jwt.ExpiredSignatureError:
        raise credential_exception
    except jwt.InvalidTokenError:
        raise credential_exception
    
    existing_user = db.query(User).filter(User.username==token_data.username).first()
    if existing_user is None:
        raise credential_exception
    
    return existing_user

@user_router_tms.post("/register", response_model=UserResponse)
def create_user(user:UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username==user.username).first()
    if existing_user:
        raise HTTPException(status_code=400,detail="username already exists")
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@user_router_tms.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == form_data.username).first()
    if not db_user or not pwd_context.verify(form_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@user_router_tms.get("/users/me/",response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
    

