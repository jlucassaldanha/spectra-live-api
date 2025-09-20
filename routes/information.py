from fastapi import APIRouter, Depends, HTTPException, Query
from utils import get_session, get_current_user, twitch_get_endpoint

from sqlalchemy.orm import Session
from models import User, TwitchUsers, UnviewUsers
from schemas import UserIdSchema

information_router = APIRouter(prefix="/information", tags=["Information"])

@information_router.get("/mods")
async def get_moderators(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
	mods_info_data = []
	all_mods_ids = []

	cursor = True
	while cursor:
		params = {
			"broadcaster_id": current_user.twitch_id,
			"first": 100
		}

		if isinstance(cursor, str):
			params["after"] = cursor

		mods = await twitch_get_endpoint(
			current_user=current_user,
			session=session,
			endpoint="https://api.twitch.tv/helix/moderation/moderators",
			params=params
		)

		mods_ids = [mod["user_id"] for mod in mods["data"]]
		all_mods_ids += mods_ids

		cursor = dict(mods["pagination"]).get("cursor", False)

		if len(mods_ids) > 0:
			mods_info = await twitch_get_endpoint(
				current_user=current_user,
				session=session,
				endpoint="https://api.twitch.tv/helix/users",
				params={"id":mods_ids}
			)

			mods_info_data += mods_info["data"]

	for mod in mods_info_data:
		twitch_user = session.query(TwitchUsers).filter(TwitchUsers.twitch_id==mod["id"]).first()
		if not twitch_user:
			twitch_user = TwitchUsers(
				mod["id"],
				mod["login"],
				mod["display_name"],
				mod["profile_image_url"]
			)
			session.add(twitch_user)
	session.commit()

	moderators = session.query(TwitchUsers).filter(TwitchUsers.twitch_id.in_(all_mods_ids)).all()

	return moderators

@information_router.get("/user")
async def get_user(display_name: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
	login = display_name.lower()
	user = session.query(TwitchUsers).filter(TwitchUsers.login == login).first()

	if not user:
		user = await twitch_get_endpoint(
			current_user=current_user,
			session=session,
			endpoint="https://api.twitch.tv/helix/users",
			params={"login": login}
		)
		
		if len(user["data"]) < 1:
			raise HTTPException(status_code=404, detail="User not found")
		
		user = user["data"][0]
		print(user)
		
		twitch_user = TwitchUsers(
				user["id"],
				user["login"],
				user["display_name"],
				user["profile_image_url"]
			)
		session.add(twitch_user)
		session.commit()

		user = session.query(TwitchUsers).filter(TwitchUsers.login == login).first()

	return user

@information_router.post("/users")
async def get_users(twitch_ids: UserIdSchema, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
	users = session.query(TwitchUsers).filter(TwitchUsers.twitch_id.in_(twitch_ids.twitch_ids)).all()

	found = {user.twitch_id for user in users}
	missing = list(set(twitch_ids.twitch_ids) - found)
	
	if len(missing) > 0:
		for i in range(0, len(missing), 100):
			ids = missing[i:i + 100]
			print(ids)
			response = await twitch_get_endpoint(
				current_user=current_user,
				session=session,
				endpoint="https://api.twitch.tv/helix/users",
				params={"id":ids}
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

	return users

@information_router.get("/viewers")
async def get_viewers(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
	unview_users = session.query(UnviewUsers).filter(UnviewUsers.channel_id==current_user.twitch_id).all()
	unview_ids = [str(unview.twitch_user_id) for unview in unview_users]

	chatters_ids = []
	cursor = True
	while cursor:
		params = {
			"broadcaster_id": current_user.twitch_id, 
			"moderator_id": current_user.twitch_id,
			"first": 1000
		}

		if isinstance(cursor, str):
			params["after"] = cursor

		chatters = await twitch_get_endpoint(
			current_user=current_user,
			session=session,
			endpoint="https://api.twitch.tv/helix/chat/chatters",
			params=params
		)

		cursor = dict(chatter["pagination"]).get("cursor", False)
	
		for chatter in chatters["data"]:
			if not chatter["user_id"] in unview_ids: 
				if chatter["user_id"] != str(current_user.twitch_id):
					chatters_ids.append(chatter["user_id"])

	users = []
	moderators_ids = []
	
	for i in range(0, len(chatters_ids), 100):
		ids = chatters_ids[i:i + 100]

		users_response = await twitch_get_endpoint(
			current_user=current_user,
			session=session,
			endpoint="https://api.twitch.tv/helix/users",
			params={"id":ids}
		)

		users += users_response["data"]

		moderators = await twitch_get_endpoint(
			current_user=current_user,
			session=session,
			endpoint="https://api.twitch.tv/helix/moderation/moderators",
			params = {
				"broadcaster_id": current_user.twitch_id, 
				"user_id": ids,
				"first": 100
			}
		)

		moderators_ids += [moderator["user_id"] for moderator in moderators["data"]]

	moderators_infos = []
	chatters_infos = []
	for user in users:
		if user["id"] in moderators_ids:
			moderators_infos.append({
				"twitch_id": user["id"],
				"display_name": user["display_name"],
				"profile_image_url": user["profile_image_url"]
			})
		else:
			chatters_infos.append({
				"twitch_id": user["id"],
				"display_name": user["display_name"],
				"profile_image_url": user["profile_image_url"]
			})

	return {
		"chatters": {
			"data": chatters_infos, 
			"total": len(chatters_infos)
			},
		"moderators": {
			"data": moderators_infos, 
			"total": len(moderators_infos)
			}
	}