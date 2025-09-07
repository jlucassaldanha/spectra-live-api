from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

db_engine = create_engine(
	"sqlite:///banco.db", 
	connect_args={"check_same_thread": False}
	)

Base = declarative_base()

def init_db(drop_first: bool = False):
	if drop_first:
		Base.metadata.drop_all(bind=db_engine)

	Base.metadata.create_all(bind=db_engine)