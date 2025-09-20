from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from db import init_db
from models import User, UnviewUsers

init_db(drop_first=False)

app = FastAPI(
	title="Spectra Live API",
	version="1.0.0"
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=[
		"https://spectralive.vercel.app",
		"http://localhost:5173"
		],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"]
)


from routes import auth_router, preferences_router, information_router

app.include_router(auth_router)
app.include_router(preferences_router)
app.include_router(information_router)