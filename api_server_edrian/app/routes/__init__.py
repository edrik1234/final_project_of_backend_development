from fastapi import APIRouter

from .auth import router as auth_router
from .requests import router as requests_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(requests_router)
