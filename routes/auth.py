from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
import requests
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from main import CLIENT_ID, CLIENT_SECRET

REDIRECT_URI = "http://localhost:8000/auth/callback"
#REDIRECT_URI = "http://localhost:5173/auth/callback"
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
def callback(request: Request, code: str, error: str = None):

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

	# Colocar em uma rota diferente, passar a usar rotas protegidas 
	user_response = requests.get(
		"https://api.twitch.tv/helix/users",
		headers={
			"Authorization": f"Bearer {auth_response["access_token"]}",
			"Client-Id": CLIENT_ID,
		}
	)

	#print("USERS DEBUG:", user_response.status_code, user_response.text)

	if user_response.status_code != 200:
		raise HTTPException(status_code=user_response.status_code, detail="Erro ao obter dados do usuário")
	
	user_response = user_response.json()
	
	return {
		"auth": auth_response,
		"user": user_response
	}