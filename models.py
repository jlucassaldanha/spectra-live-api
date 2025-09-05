from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey

db_url = "sqlite:///banco.db"
engine = create_engine(db_url)

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    twitch_id = Column("twitch_id", Integer, unique=True)
    username = Column("username", String, unique=True)
    token = Column("token", String)
    refresh_token = Column("refresh_token", String)
    expire_time = Column("expire_time", Integer)

    def __init__(self, twitch_id: int, username: str, token: str, refresh_token: str, expire_time: int):
        self.twitch_id = twitch_id
        self.username = username
        self.token = token
        self.refresh_token = refresh_token
        self.expire_time = expire_time

class Blocked(Base):
    __tablename__ = "blocked"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    twitch_id = Column("twitch_id", Integer, unique=True)
    username = Column("username", String)
    user_id = Column("user_id", Integer, ForeignKey("user.id"))

    def __init__(self, twitch_id: int, username: str, user_id: int):
        self.twitch_id = twitch_id
        self.username = username
        self.user_id = user_id

