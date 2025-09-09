import httpx
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from main import CLIENT_ID, CLIENT_SECRET
from models import User
from .dependecies import get_session

async def refresh_twitch_token(refresh_token: str, user_id: int = None, session: Session = Depends(get_session)):
	async with httpx.AsyncClient() as client:
		response = await client.post(
			"https://id.twitch.tv/oauth2/token",
			params={
				"grant_type": "refresh_token",
				"refresh_token": refresh_token,
				"client_id": CLIENT_ID,
				"client_secret": CLIENT_SECRET
			}
		)

	if response.status_code != 200:
		raise HTTPException(status_code=401, detail="Falha ao usar refresh token")
	
	tokens = response.json()

	if not user_id:
		return tokens
	
	user = session.query(User).filter(User.id==user_id).first()

	if not user:
		HTTPException(status_code=404, detail="Usuário não encontrado")

	user.access_token = tokens["access_token"]
	user.refresh_token = tokens["refresh_token"]
	user.expires_in = tokens["expires_in"]

	session.commit()

	return user

async def refresh_twitch_token_deprecated(user_id: int, session: Session = Depends(get_session)):
	user = session.query(User).filter(User.id==user_id).first()

	if not user:
		HTTPException(status_code=404, detail="Usuário não encontrado")

	async with httpx.AsyncClient() as client:
		response = await client.post(
			"https://id.twitch.tv/oauth2/token",
			params={
				"grant_type": "refresh_token",
				"refresh_token": user.refresh_token,
				"client_id": CLIENT_ID,
				"client_secret": CLIENT_SECRET
			}
		)

	if response.status_code != 200:
		raise HTTPException(status_code=401, detail="Falha ao usar refresh token")
	
	tokens = response.json()
	user.access_token = tokens["access_token"]
	user.refresh_token = tokens["refresh_token"]
	user.expires_in = tokens["expires_in"]

	session.commit()

	return user