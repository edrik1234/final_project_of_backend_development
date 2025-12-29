from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from pydantic import BaseModel
from typing import Optional, List
import logging
from shared_edrian.models.data_base import SessionLocal
from shared_edrian.models.models import User
import os
log = logging.getLogger("shared_edrian.security.auth.py")
logging.basicConfig(level=logging.WARNING)


class Token_Data(BaseModel):
    username: Optional[str] | None = None

SECRET_KEY = os.getenv("JWT_SECRET", os.getenv("DEEPSEEK_API_KEY", "CHANGE_ME_SECRET"))
ALGORITHM = "HS256"
TOKEN_EXPIRES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_access_token(username: str):
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> Token_Data:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # ✔ FIXED
        username: str = payload.get("sub")
        if username is None:
               raise HTTPException(status_code=401, detail="invalid token")
        return Token_Data(username=username)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
        )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db = Depends(get_db)
    ):
    try:
        token_data = verify_token(token)
        user = db.query(User).filter(User.username == token_data.username).first()
       # payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
      #  username = payload.get("sub")
        if not user:
            raise HTTPException(status_code=401, detail="user not found")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
