import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from main import CLIENT_ID, CLIENT_SECRET
from models import User

async def refresh_twitch_token(refresh_token: str, session: Session, user_id: int = None):
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
		raise HTTPException(status_code=404, detail="Usuário não encontrado")

	user.access_token = tokens["access_token"]
	user.refresh_token = tokens["refresh_token"]
	user.expires_in = tokens["expires_in"]

	session.commit()
	session.refresh(user)

	return user

async def twitch_get_endpoint(current_user: User, session: Session, endpoint: str, params: dict = None):
	async with httpx.AsyncClient() as client:
		async def get_request(token):
			return await client.get(
				url=endpoint,
				headers={
					"Authorization": f"Bearer {token}",
					"Client-Id": CLIENT_ID,
				},
				params=params
			)
		
		response = await get_request(current_user.access_token)

		if response.status_code == 401:
			current_user = await refresh_twitch_token(refresh_token=current_user.refresh_token, user_id=current_user.id, session=session)

			response = await get_request(current_user.access_token)

	if response.status_code != 200:
		raise HTTPException(status_code=response.status_code, detail="Erro ao obter dados")
	
	return response.json()