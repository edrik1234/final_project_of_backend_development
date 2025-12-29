from sqlalchemy import Column, Integer, String, Text , TIMESTAMP, BigInteger, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import pprint
import six
import typing
from shared_edrian.helpful_utils import util
import logging
import datetime
from datetime import datetime
T = typing.TypeVar('T')
Base = declarative_base()



log = logging.getLogger("models.py")
log.setLevel(logging.WARNING)


class TelegramUser(Base):
    __tablename__ = "telegram_users"

    telegram_id = Column(BigInteger, primary_key=True)
    username = Column(String)
    state = Column(String, nullable=False)
    request_id = Column(Integer)
    questions = Column(Text)
    answers = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, onupdate=func.now())


class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, index=True)
    questions = Column(Text)
    answers = Column(Text)
    result = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique =True , nullable =False)
    password = Column(String, nullable=False)

class RequestStatus(Base):
    __tablename__ = "requests_status"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(20), nullable=False)
    result = Column(Text)

    @classmethod
    def from_dict(cls: typing.Type[T], dikt) -> T:
        return util.deserialize_model(dikt, cls)

    def to_dict(self):
        result = {}
        for attr, _ in six.iteritems(getattr(self, "swagger_types", {})):
            value = getattr(self, attr, None)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        return result

    def to_str(self):
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        return self.to_str()

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
