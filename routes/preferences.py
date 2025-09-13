from fastapi import APIRouter, Depends, HTTPException

from utils import get_session, get_current_user, twitch_get_endpoint

from sqlalchemy.orm import Session
from models import User, TwitchUsers, UnviewUsers
from schemas import UserIdSchema

preferences_router = APIRouter(prefix="/preferences", tags=["Preferences"])

@preferences_router.post("/add/unview")
async def set_unview(twitch_ids: UserIdSchema, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):	
	users = session.query(TwitchUsers).filter(TwitchUsers.twitch_id.in_(twitch_ids.twitch_ids)).all()

	found = {user.twitch_id for user in users}
	missing = set(twitch_ids.twitch_ids) - found

	if len(missing) > 0:
		response = await twitch_get_endpoint(
			current_user=current_user,
			session=session,
			endpoint="https://api.twitch.tv/helix/users",
			params={"id":missing}
		)

		for data in response["data"]:
			new_twitch_user = TwitchUsers(
				data["id"],
				data["login"],
				data["display_name"],
				data["profile_image_url"]
			)
			session.add(new_twitch_user)

		session.commit()

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

	return twitch_ids

@preferences_router.delete("/remove/unview")
async def remove_unview(twitch_ids: UserIdSchema, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):	
	users = session.query(TwitchUsers).filter(TwitchUsers.twitch_id.in_(twitch_ids.twitch_ids)).all()

	for user in users:
		unview = session.query(UnviewUsers).filter(UnviewUsers.channel_id==current_user.twitch_id).filter(UnviewUsers.twitch_user_id==user.twitch_id).first()
		if unview:
			session.delete(unview)

	session.commit()

	return twitch_ids

@preferences_router.get("/list/unview")
async def get_unview(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
	unviews = session.query(UnviewUsers).filter(UnviewUsers.channel_id==current_user.twitch_id).all()

	return unviews