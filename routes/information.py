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

	mods_ids = []
	mods_infos = []
	for mod in mods["data"]:
		twitch_user = session.query(TwitchUsers).filter(TwitchUsers.twitch_id==mod["user_id"]).first()
		if not twitch_user:
			mods_ids.append(mod["user_id"])
		else:
			twitch_user = twitch_user.__dict__
			mods_infos.append(twitch_user)

	if len(mods_ids) > 0:
		users_infos = await twitch_get_endpoint(
			current_user=current_user,
			session=session,
			endpoint="https://api.twitch.tv/helix/users",
			params={"id":mods_ids}
		)

		for user_info in users_infos["data"]:
			new_twitch_user = TwitchUsers(
				user_info["id"],
				user_info["login"],
				user_info["display_name"],
				user_info["profile_image_url"]
			)
			session.add(new_twitch_user)

			twitch_user = new_twitch_user.__dict__
			mods_infos.append(twitch_user)

		session.commit()
	
	print(mods_infos)
	# Adicionar os moderadores na tabela de moderadores (na vdd não salvar moderadores no banco de dados. eles podem mudar)

	return mods_infos