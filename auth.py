import jwt
import bcrypt
import os
from datetime import datetime, timedelta
from db import db_manager
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from functools import wraps

load_dotenv()

JWT_SECRET = os.getenv("JWT_KEY") 
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_MINUTES = 60
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def register_user(username: str, password: str, role: str) -> bool:
    return db_manager.register_user(username, password, role)

def create_tokens(username: str, role: str):
    access_token = create_access_token({"sub": username, "role": role})
    refresh_token = create_refresh_token({"sub": username, "role": role})
    return access_token, refresh_token
    
def authenticate_user(username: str, password: str):
    user = db_manager.collections["users"].find_one({"username": username})
    if not user or not bcrypt.checkpw(password.encode(), user["password"]):
        return None

    # Create tokens
    access_token = create_access_token({"username": username, "role": user["role"]})
    refresh_token = create_refresh_token({"username": username})

    # Store refresh token in DB
    db_manager.store_refresh_token(username, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "role": user["role"]
    }

def decode_token(token: str) -> dict:
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    if db_manager.is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="Token has been blacklisted")

    try:
        return decode_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
def admin_only_route(route_func):
    @wraps(route_func)
    async def wrapper(*args, user: dict = Depends(get_current_user), **kwargs):
        if user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        return await route_func(*args, user=user, **kwargs)
    return wrapper