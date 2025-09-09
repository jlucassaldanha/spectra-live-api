from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey

from db import Base

class User(Base):
    __tablename__ = "user"
    
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    access_token = Column("access_token", String)
    refresh_token = Column("refresh_token", String)
    expires_in = Column("expires_in", Integer)
    twitch_id = Column("twitch_id", Integer, unique=True)
    login = Column("login", String)
    display_name = Column("display_name", String)
    email = Column("email", String)
    profile_image_url = Column("profile_image_url", String)

    def __init__(self, access_token: str, refresh_token: str, expires_in: int, twitch_id: int, login: str, display_name: str, email: str, profile_image_url: str):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_in = expires_in
        self.twitch_id = twitch_id
        self.login = login
        self.display_name = display_name
        self.email = email
        self.profile_image_url = profile_image_url

class UnviewUsers(Base):
    __tablename__ = "unview_users"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    user_id = Column("user_id", ForeignKey("user.id"))
    twitch_id = Column("twitch_id", Integer)
    login = Column("login", String)
    display_name = Column("display_name", String)
    profile_image_url = Column("profile_image_url", String)

    def __init__(self, user_id: int, twitch_id: int, login: str, display_name: str, profile_image_url: str):
        self.user_id = user_id
        self.twitch_id = twitch_id
        self.login = login
        self.display_name = display_name
        self.profile_image_url = profile_image_url