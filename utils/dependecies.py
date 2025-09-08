from fastapi import Depends, Request, HTTPException
from sqlalchemy.orm import sessionmaker, Session

from models import User
from db import db_engine

SessionLocal = sessionmaker(bind=db_engine)

def get_session():
	# Cria a sessão para poder manipular o banco de dados
	try:
		session = SessionLocal()

		# "Retorna" a sessão para ser utilizada fora desta função
		yield session 
	finally: # Ao final da utilização, fecha a sessão
		session.close()


