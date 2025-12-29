import os
import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt
from shared_edrian.security.auth import get_current_user, verify_token
from typing import Optional, List
import typing
from shared_edrian.models.data_base import SessionLocal
from shared_edrian.models.models import RequestStatus, User
from api_server_edrian.app.producer import send_message
from shared_edrian.security.auth import Token_Data
import shared_edrian.security.auth
log = logging.getLogger("api.routes.requests")
logging.basicConfig(level=logging.WARNING)
router = APIRouter(prefix="/requests", tags=["requests_me"])

JWT_SECRET = os.getenv("JWT_SECRET", os.getenv("DEEPSEEK_API_KEY", "CHANGE_ME_SECRET"))

class UserRequest(BaseModel):
    text: str

class RequestResponse(BaseModel):
    request_id: int

class ResultResponse(BaseModel):
    status: str
    result: str | None = None


#class Token_Data(BaseModel):
    #user_name: Optional[str] = None

@router.post("/request", response_model=RequestResponse)
def send_user_request(request: UserRequest, user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        db_request = RequestStatus(status="in_progress", result=None)
        db.add(db_request)
        db.commit()
        db.refresh(db_request)

        send_message("user_requests", {
            "request_id": db_request.id,
            "text": request.text
        })

        return RequestResponse(request_id=db_request.id)
    finally:
        db.close()


@router.get("/result/{request_id}", response_model=ResultResponse)
def get_request_result(request_id: int, user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        db_request = db.query(RequestStatus).filter(RequestStatus.id == request_id).first()
        if not db_request:
            raise HTTPException(status_code=404, detail="Request not found")
        if db_request.status in ("done", "fail"):
            result = db_request.result
            db.delete(db_request)
            db.commit()
            return ResultResponse(status=db_request.status, result=result)
        else:
            return ResultResponse(status="in_progress", result=None)
    finally:
        db.close()
