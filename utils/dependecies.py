from fastapi import Depends, Request, HTTPException
from sqlalchemy.orm import sessionmaker, Session

from models import User
from db import db_engine

from .token import decode_jwt

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


SessionLocal = sessionmaker(bind=db_engine)

async def get_session():
	try:
		session = SessionLocal()

		yield session 
	finally:
		session.close()
		
async def get_current_user(request: Request, session: Session = Depends(get_session)):
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

security = HTTPBearer()

def get_current_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session) # Injetamos a sessão do banco aqui
):
    token = credentials.credentials

    try:
        user_data = decode_jwt(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    db_user = session.query(User).filter(User.twitch_id == user_data["twitch_id"]).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado no banco")

    return db_user


