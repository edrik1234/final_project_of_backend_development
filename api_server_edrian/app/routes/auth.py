from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import logging
from shared_edrian.models.models import User
from shared_edrian.security.auth import Token_Data
from datetime import datetime, timedelta
import shared_edrian.security.auth
from shared_edrian.security.auth import (
    get_db,
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    get_current_user
)


TOKEN_EXPIRES = 60
log = logging.getLogger("api.routes.auth")
logging.basicConfig(level=logging.WARNING)
router = APIRouter(prefix="/auth", tags=["auth_me"])

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

@router.post("/register")
def register(user: RegisterRequest, db = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=409, detail="User exists")
    hashed_pwd = hash_password(user.password)
    user = User(
        username=user.username,
        email=user.email,
        password=hashed_pwd
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id" : user.id,
            "username" : user.username,
            "email" : user.email,
            }


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(
        user.username
    )
    return {"access_token": token, "token_type": "bearer"}


