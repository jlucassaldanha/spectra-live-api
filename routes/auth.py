from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
import requests

from main import CLIENT_ID, CLIENT_SECRET
from utils import get_session, get_user

from sqlalchemy.orm import Session
from models import TwitchUser, TwitchUserProfile

REDIRECT_URI = "http://localhost:8000/auth/callback"
#REDIRECT_URI = "https://spectralive.vercel.app/auth/callback"

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.get("/login")
def login():
	url = (
        "https://id.twitch.tv/oauth2/authorize"
		f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=user:read:email"
    )
	
	return RedirectResponse(url)

@auth_router.get("/callback")
def callback(code: str, error: str = None, session: Session = Depends(get_session)):

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

	twitch_user = TwitchUser(
		auth_response["access_token"],
		auth_response["refresh_token"],
		auth_response["expires_in"]
		)
	session.add(twitch_user)
	session.commit()

	redirect_response = RedirectResponse(url="http://localhost:5173/profile")
	redirect_response.set_cookie("user_id", twitch_user.id, httponly=True, secure=False)

	return redirect_response

@auth_router.get("/me")
def me(user: TwitchUser = Depends(get_user), session: Session = Depends(get_session)):
	user_response = requests.get(
		"https://api.twitch.tv/helix/users",
		headers={
			"Authorization": f"Bearer {user.access_token}",
			"Client-Id": CLIENT_ID,
		}
	)

	#print("USERS DEBUG:", user_response.status_code, user_response.text)

	if user_response.status_code != 200:
		raise HTTPException(status_code=user_response.status_code, detail="Erro ao obter dados do usuário")
	
	user_response = user_response.json()["data"][0]

	twitch_user_profile = TwitchUserProfile(
		user.id,
		user_response["id"],
		user_response["login"],
		user_response["display_name"],
		user_response["email"],
		user_response["profile_image_url"],
	)
	session.add(twitch_user_profile)
	session.commit()

	return user_response

