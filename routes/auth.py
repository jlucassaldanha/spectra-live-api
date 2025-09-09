from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse

import httpx, uuid

from main import CLIENT_ID, CLIENT_SECRET
from utils import get_session, create_jwt, get_current_user, refresh_twitch_token

from sqlalchemy.orm import Session
from models import User

REDIRECT_URI = "http://localhost:8000/auth/callback"
#REDIRECT_URI = "https://spectralive.vercel.app/auth/callback"

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

sessions = {}

@auth_router.get("/login")
async def login():
	url = (
        "https://id.twitch.tv/oauth2/authorize"
		f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=user:read:email moderation:read"
    )
	
	return RedirectResponse(url)

@auth_router.get("/callback")
async def callback(code: str, error: str = None):

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

	auth_response = auth_response.json()

	session_token = str(uuid.uuid4())

	sessions[session_token] = {
		"access_token": auth_response["access_token"],
		"refresh_token": auth_response["refresh_token"],
		"expires_in": auth_response["expires_in"]
	}

	redirect_response = RedirectResponse(url="https://localhost:5173/dashboard")
	redirect_response.set_cookie(
		key="session_token",
		value=session_token,
		httponly=True,
		secure=True,
		samesite="lax"
	)

	return redirect_response


@auth_router.get("/me")
async def me(request: Request, session: Session = Depends(get_session)):

	session_token = request.cookies.get("session_token")

	if not session_token or session_token not in sessions:
		raise HTTPException(status_code=401, detail="Não autenticado")
	
	user_tokens = sessions[session_token]

	async with httpx.AsyncClient() as client:
		async def get_info(token):
			return await client.get(
				"https://api.twitch.tv/helix/users",
				headers={
					"Authorization": f"Bearer {token}",
					"Client-Id": CLIENT_ID,
				}	
			)
		
		user_response = await get_info(user_tokens["access_token"])

		if user_response.status_code == 401:
			user_tokens = await refresh_twitch_token(refresh_token=user_tokens["refresh_token"], session=session)
			
			user_response = await get_info(user_tokens["access_token"])

	if user_response.status_code != 200:
		raise HTTPException(status_code=user_response.status_code, detail="Erro ao obter dados do usuário")
	
	user_response = user_response.json()["data"][0]

	twitch_user = session.query(User).filter(User.twitch_id==user_response["id"]).first()

	if not twitch_user:
		twitch_user = User(
			user_tokens["access_token"],
			user_tokens["refresh_token"],
			user_tokens["expires_in"],
			user_response["id"],
			user_response["login"],
			user_response["display_name"],
			user_response["email"],
			user_response["profile_image_url"],
		)
		session.add(twitch_user)

	elif twitch_user:
		twitch_user.access_token = user_tokens["access_token"]
		twitch_user.refresh_token = user_tokens["refresh_token"]
		twitch_user.expires_in = user_tokens["expires_in"]
	
	session.commit()

	del sessions[session_token]

	jwt = create_jwt(twitch_user.id, twitch_user.twitch_id)

	response = JSONResponse({"msg": "Usuario autenticado"})
	response.set_cookie(
		key="auth_token",
		value=jwt,
		httponly=True,
		secure=True,
		samesite="lax"
	)

	return response

@auth_router.post("/logout")
async def logout():
	redirect_response = RedirectResponse(url="https://localhost:5173/home")
	redirect_response.delete_cookie("auth_token")
	return redirect_response

@auth_router.get("/logout-get")
async def logout_get():
	redirect_response = RedirectResponse(url="https://localhost:5173/home")
	redirect_response.delete_cookie("auth_token")
	return redirect_response

@auth_router.get("/user-info")
async def user_info(user: User = Depends(get_current_user)):
	return {
		"login":user.login,
		"id": user.id
	}

