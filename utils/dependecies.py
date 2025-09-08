from fastapi import Depends, Request, HTTPException
from sqlalchemy.orm import sessionmaker, Session

from models import User
from db import db_engine

from .token import decode_jwt

SessionLocal = sessionmaker(bind=db_engine)

def get_session():
	# Cria a sessão para poder manipular o banco de dados
	try:
		session = SessionLocal()

		# "Retorna" a sessão para ser utilizada fora desta função
		yield session 
	finally: # Ao final da utilização, fecha a sessão
		session.close()
		
def get_current_user(request: Request, session: Session = Depends(get_session)):
	token = request.cookies.get("auth_token")
	if not token:
		raise HTTPException(status_code=401, detail="Não autenticado")
	
	payload = decode_jwt(token)
	if not payload:
		raise HTTPException(status_code=401, detail="Token inválido")
	
	user_id = payload["user_id"]
	if not user_id:
		raise HTTPException(status_code=401, detail="Token inválido, sem ID de usuário")
	
	user = session.query(User).filter(User.id==user_id).first()
	if not user:
		raise HTTPException(status_code=404, detail="Usuário não encontrado")
	
	return user


