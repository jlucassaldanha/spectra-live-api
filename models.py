from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey

from db import Base

class TwitchUser(Base):
    __tablename__ = "twitch_user"
    
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    access_token = Column("access_token", String)
    refresh_token = Column("refresh_token", String)
    expire_in = Column("expire_in", Integer)

    user_profile = relationship("TwitchUserProfile", back_populates="user", uselist=False)

    def __init__(self, access_token: str, refresh_token: str, expire_in: int):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expire_in = expire_in

class TwitchUserProfile(Base):
    __tablename__ = "twitch_user_profile"

    id = Column("id", ForeignKey("twitch_user.id"), primary_key=True)
    twitch_id = Column("twitch_id", Integer, unique=True)
    login = Column("login", String)
    display_name = Column("display_name", String)
    email = Column("email", String)
    profile_img_url = Column("profile_img_url", String)

    user = relationship("TwitchUser", back_populates="user_profile")

    def __init__(self, id: int, twitch_id: int, login: str, display_name: str, email: str, profile_img_url: str,):
        self.id = id
        self.twitch_id = twitch_id
        self.login = login
        self.display_name = display_name
        self.email = email
        self.profile_img_url = profile_img_url


