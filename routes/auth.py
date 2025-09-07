from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse

import requests
import uuid
from datetime import datetime, timedelta

from main import CLIENT_ID, CLIENT_SECRET
from utils import get_session, get_user

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
        "&scope=user:read:email"
    )
	
	return RedirectResponse(url)

@auth_router.get("/callback")
async def callback(code: str, response: Response, error: str = None):

	if error:
		raise HTTPException(status_code=401, detail="Usuário não autorizado")
	
	auth_response = requests.post(
		"https://id.twitch.tv/oauth2/token",
		params={
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
def me(request: Request, session: Session = Depends(get_session)):

	session_token = request.cookies.get("session_token")

	if not session_token or session_token not in sessions:
		raise HTTPException(status_code=401, detail="Não autenticado")
	
	user_tokens = sessions[session_token]

	user_response = requests.get(
		"https://api.twitch.tv/helix/users",
		headers={
			"Authorization": f"Bearer {user_tokens["access_token"]}",
			"Client-Id": CLIENT_ID,
		}
	)

	#print("USERS DEBUG:", user_response.status_code, user_response.text)

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
		session.commit()

	del sessions[session_token]

	return {
		"id":twitch_user.id,
		"data": twitch_user
	}

