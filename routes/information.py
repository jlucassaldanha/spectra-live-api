from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse

import httpx, uuid

from main import CLIENT_ID, CLIENT_SECRET
from utils import get_session, create_jwt, decode_jwt, get_current_user, refresh_twitch_token

from sqlalchemy.orm import Session
from models import User

information_router = APIRouter(prefix="/information", tags=["Information"])

@information_router.get("/mods")
async def get_moderators(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
	
	async with httpx.AsyncClient() as client:
		async def get_mods(token):
			return await client.get(
				"https://api.twitch.tv/helix/moderation/moderators",
				headers={
					"Authorization": f"Bearer {token}",
					"Client-Id": CLIENT_ID,
				},
				params={"broadcaster_id": current_user.twitch_id}
			)
		
		mods_response = await get_mods(current_user.access_token)

		if mods_response.status_code == 401:
			current_user = await refresh_twitch_token(refresh_token=current_user.refresh_token, user_id=current_user.id, session=session)

			mods_response = await get_mods(current_user.access_token)

	if mods_response.status_code != 200:
		raise HTTPException(status_code=mods_response.status_code, detail="Erro ao obter dados")
	
	return mods_response.json()