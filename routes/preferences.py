from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse

import httpx, uuid

from main import CLIENT_ID, CLIENT_SECRET
from utils import get_session, create_jwt, decode_jwt, get_current_user, refresh_twitch_token, twitch_get_endpoint

from sqlalchemy.orm import Session
from models import User, TwitchUsers

preferences_router = APIRouter(prefix="/preferences", tags=["Preferences"])

# Lista moderadores para poder colocar na lista de fora de vista
preferences_router.get("/unview")
async def get_moderators(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
	
	pass