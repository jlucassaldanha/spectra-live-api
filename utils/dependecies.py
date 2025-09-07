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

def get_user(request: Request, session: Session = Depends(get_session)):
	user_id = request.cookies.get("user_id")

	if not user_id:
		raise HTTPException(status_code=401, detail="Não autenticado")
	
	twitch_user = session.query(User).filter(User.id==user_id).first()

	if not twitch_user:
		raise HTTPException(status_code=401, detail="Não autenticado")
	
	return twitch_user