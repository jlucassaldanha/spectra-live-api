from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from main import CLIENT_ID, CLIENT_SECRETS, REDIRECT_URI
import requests

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

@auth_router.get("/login")
def login():
	auth_url = (
        "https://id.twitch.tv/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=user:read:email"
    )
	
	return RedirectResponse(auth_url)

@auth_router.get("/callback")
def callback(request: Request, code: str):
	response = requests.post(
		"https://id.twitch.tv/oauth2/token",
		params={
			"client_id": CLIENT_ID,
			"client_secret": CLIENT_SECRETS,
			"code": code,
			"grant_type": "authorization_code",
			"redirect_uri": REDIRECT_URI
		}
	).json()

	access_token = response.get("access_token")

	if not access_token:
		return HTTPException(status_code=400, detail="Falha ao obter token")
	
	headers = {
		"Authorization": f"Baerer {access_token}",
		"Client_Id": CLIENT_ID
	}

	user_info = requests.get("https://api.twitch.tv/helix/users", headers=headers)


	# Armazena o token em memória (por ID do usuário)
	#TOKENS = {}
	#user_id = user_info["data"][0]["id"]
	#TOKENS[user_id] = access_token

	print(user_info, access_token)

	# Redireciona de volta para o frontend já logado
	#return RedirectResponse(f"http://localhost:8000/loggedin?user_id={user_id}")
	return {
		"user_info": user_info.json(),
		"access_token": access_token
	}