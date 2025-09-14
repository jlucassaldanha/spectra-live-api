from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_INTERNAL_URL") or os.getenv("DATABASE_URL") or "sqlite:///./banco.db"

if DATABASE_URL.startswith("sqlite"):
	db_engine = create_engine(
		DATABASE_URL, 
		connect_args={"check_same_thread": False}
		)
else:
	db_engine = create_engine(DATABASE_URL)

Base = declarative_base()

def init_db(drop_first: bool = False):
	if drop_first:
		Base.metadata.drop_all(bind=db_engine)

	Base.metadata.create_all(bind=db_engine)