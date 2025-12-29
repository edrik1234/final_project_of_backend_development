import os
from sqlalchemy import create_engine #create engine of data base
from sqlalchemy.orm import sessionmaker #the way the db make interactions with SQL and creatin session class
import shared_edrian.models.models as our_models
import logging
DATABASE_URL = os.getenv("DB_URL", "postgresql://edrian:Edrik5500@postgres:5432/requests")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
our_models.Base.metadata.create_all(bind=engine)


log = logging.getLogger("data_base.py")
log.setLevel(logging.WARNING)


