from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse

import httpx, uuid

from main import CLIENT_ID, CLIENT_SECRET
from utils import get_session, create_jwt, decode_jwt, get_current_user, refresh_twitch_token, twitch_get_endpoint

from sqlalchemy.orm import Session
from models import User, TwitchUsers

information_router = APIRouter(prefix="/information", tags=["Information"])

@information_router.get("/mods")
async def get_moderators(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
	
	mods = await twitch_get_endpoint(
		current_user=current_user,
		session=session,
		endpoint="https://api.twitch.tv/helix/moderation/moderators",
		params={"broadcaster_id": current_user.twitch_id}
	)

	mods_ids = [mod["user_id"] for mod in mods["data"]]

	mods_info = await twitch_get_endpoint(
		current_user=current_user,
		session=session,
		endpoint="https://api.twitch.tv/helix/users",
		params={"id":mods_ids}
	)

	for mod in mods_info["data"]:
		user = session.query(TwitchUsers).filter(TwitchUsers.twitch_id==mod["id"]).first()
		if not user:
			new_twitch_user = TwitchUsers(
				mod["id"],
				mod["login"],
				mod["display_name"],
				mod["profile_image_url"]
			)
			session.add(new_twitch_user)
	
	session.commit()

	moderators = session.query(TwitchUsers).filter(TwitchUsers.twitch_id.in_(mods_ids)).all()

	return moderators
