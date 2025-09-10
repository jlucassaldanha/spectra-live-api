from pydantic import BaseModel

class UserIdSchema(BaseModel):
	twitch_ids: list[int]