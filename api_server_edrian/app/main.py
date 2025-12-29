from fastapi import FastAPI
from api_server_edrian.app.routes import router
import logging
from threading import Thread
#from bot.app.telegram_bot import run_bot
#from contextlib import asynccontextmanager
from api_server_edrian.app.routes import auth, requests
from api_server_edrian.app.routes import router

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger("main_of_producer")

app = FastAPI(
    title = "Lean API Worker System(trivia game)", #application name,
    version="1.0.0", #application version,
    description=  "A lean messaging system with API-to-worker communication via Kafka" ,  #application description,
    docs_url="/docs" , #url to swagger ui documentaion,
    redoc_url="/redoc" , #url to redoc ui documentaion
)
app.include_router(router)
app.include_router(auth.router)
app.include_router(requests.router)