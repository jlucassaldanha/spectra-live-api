from fastapi import APIRouter, Depends

from utils import get_session, get_current_user, twitch_get_endpoint

from sqlalchemy.orm import Session
from models import User, UnviewUsers
from schemas import UserIdSchema

preferences_router = APIRouter(prefix="/preferences", tags=["Preferences"])

@preferences_router.post("/add/unview")
async def set_unview(twitch_ids: UserIdSchema, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):	
	
	twitch_users_ids = []
	for i in range(0, len(twitch_ids.twitch_ids), 100):
		ids = twitch_ids.twitch_ids[i:i + 100]
		
		response = await twitch_get_endpoint(
			current_user=current_user,
			session=session,
			endpoint="https://api.twitch.tv/helix/users",
			params={"id":ids}
		)

		data = response["data"]
		twitch_users_ids += [user["id"] for user in data]
		

	for id in twitch_users_ids:
		unview = session.query(UnviewUsers).filter(UnviewUsers.channel_id==current_user.twitch_id).filter(UnviewUsers.twitch_user_id==id).first()

		if not unview:
			new_unview = UnviewUsers(
				channel_id=current_user.twitch_id,
				twitch_user_id=id
			)
			session.add(new_unview)

	session.commit()

	return twitch_ids

@preferences_router.delete("/remove/unview")
async def remove_unview(twitch_ids: UserIdSchema, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):	

	for id in twitch_ids.twitch_ids:
		unview = session.query(UnviewUsers).filter(UnviewUsers.channel_id==current_user.twitch_id).filter(UnviewUsers.twitch_user_id==id).first()
		if unview:
			session.delete(unview)

	session.commit()

	return twitch_ids

@preferences_router.get("/list/unview")
async def get_unview(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
	unviews = session.query(UnviewUsers).filter(UnviewUsers.channel_id==current_user.twitch_id).all()

	return unviews