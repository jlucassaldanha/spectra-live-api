from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse

import httpx, uuid

from main import CLIENT_ID, CLIENT_SECRET
from utils import get_session, create_jwt, decode_jwt, get_current_user, refresh_twitch_token, twitch_get_endpoint

from sqlalchemy.orm import Session
from models import User, TwitchUsers, UnviewUsers
from schemas import UserIdSchema

preferences_router = APIRouter(prefix="/preferences", tags=["Preferences"])

# Lista moderadores para poder colocar na lista de fora de vista
@preferences_router.post("/unview")
async def set_unview(twitch_ids: UserIdSchema, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):	
	users = session.query(TwitchUsers).filter(TwitchUsers.twitch_id.in_(twitch_ids.twitch_ids)).all()

	for user in users:
		unview = session.query(UnviewUsers).filter(UnviewUsers.channel_id==current_user.twitch_id).filter(UnviewUsers.twitch_user_id==user.twitch_id).first()
		if not unview:
			new_unview = UnviewUsers(
				channel_id=current_user.twitch_id,
				twitch_user_id=user.twitch_id
			)
			session.add(new_unview)

	session.commit()

	return {"msg": "ok"}
	