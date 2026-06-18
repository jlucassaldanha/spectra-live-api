from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import httpx
from config import CLIENT_ID, CLIENT_SECRET, API_URL, FRONTEND_URL
from utils import get_session, create_jwt, decode_jwt

from sqlalchemy.orm import Session
from models import User

REDIRECT_URI = API_URL + "/auth/callback"

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

security = HTTPBearer()

sessions = {}

@auth_router.get("/login")
async def login():
	url = (
        "https://id.twitch.tv/oauth2/authorize"
		f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=user:read:email moderation:read moderator:read:chatters"
    )
	
	return RedirectResponse(url)

@auth_router.get("/callback")
async def callback(code: str, session: Session = Depends(get_session), error: str = None):

	if error:
		raise HTTPException(status_code=401, detail="Usuário não autorizado")
	
	async with httpx.AsyncClient() as client:
		auth_response = await client.post(
			"https://id.twitch.tv/oauth2/token",
			data={
				"client_id": CLIENT_ID,
				"client_secret": CLIENT_SECRET,
				"code": code,
				"grant_type": "authorization_code",
				"redirect_uri": REDIRECT_URI
			}
		)

		if auth_response.status_code != 200:
			raise HTTPException(status_code=auth_response.status_code, detail="Erro ao obter token")

		auth_data = auth_response.json()

		user_response = await client.get(
			"https://api.twitch.tv/helix/users",
				headers={
					"Authorization": f"Bearer {auth_data['access_token']}",
					"Client-Id": CLIENT_ID,
				}
		)

		if user_response.status_code != 200:
			raise HTTPException(status_code=user_response.status_code, detail="Erro ao obter dados do usuário na Twitch")
		
		twitch_user_data = user_response.json()["data"][0]
	
	db_user = session.query(User).filter(User.twitch_id == twitch_user_data["id"]).first()
	
	if not db_user:
		db_user = User(
            access_token=auth_data["access_token"],
            refresh_token=auth_data["refresh_token"],
            expires_in=auth_data["expires_in"],
            twitch_id=twitch_user_data["id"],
            login=twitch_user_data["login"],
            display_name=twitch_user_data["display_name"],
            email=twitch_user_data["email"],
            profile_image_url=twitch_user_data["profile_image_url"],
        )
		session.add(db_user)
	else:
		db_user.access_token = auth_data["access_token"]
		db_user.refresh_token = auth_data["refresh_token"]
		db_user.expires_in = auth_data["expires_in"]
		db_user.display_name = twitch_user_data["display_name"]
		db_user.profile_image_url = twitch_user_data["profile_image_url"]
		
	session.commit()
	
	jwt_token = create_jwt(db_user.id, db_user.twitch_id)
	
	return RedirectResponse(url=f"{FRONTEND_URL}/login/success?token={jwt_token}")


@auth_router.get("/me")
async def me(credentials: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_session)):

	token = credentials.credentials
	
	try:
		user_data = decode_jwt(token)
	except Exception:
		raise HTTPException(status_code=401, detail="Token inválido ou expirado")
	
	db_user = session.query(User).filter(User.twitch_id == user_data["twitch_id"]).first()
	
	if not db_user:
		raise HTTPException(status_code=401, detail="Usuário não encontrado")
	
	return JSONResponse({
        "display_name": db_user.display_name,
        "profile_image_url": db_user.profile_image_url
    })

@auth_router.post("/logout")
async def logout():

	return {"msg": "ok"}

