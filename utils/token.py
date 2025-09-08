from jose import jwt, JWTError
from datetime import datetime, timedelta
from main import SECRET_KEY, ALGORITHM
from fastapi import Depends, Request, HTTPException

def create_jwt(user_id: int, twitch_id: int):
	expire = datetime.now() + timedelta(minutes=(60*24*7))

	token = jwt.encode({
		"user_id": user_id,
		"twitch_id": twitch_id,
		"exp": expire
	}, SECRET_KEY, algorithm=ALGORITHM)

	return token

def decode_jwt(token: str):
	try:
		return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
	except JWTError:
		raise HTTPException(status_code=401, detail="Token não autenticado")
	
## Melhorar logica de criação e uso do token