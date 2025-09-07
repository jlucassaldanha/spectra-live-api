from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

app = FastAPI(
	title="Spectra Live API",
	version="1.0.0"
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=[
		"https://spectralive.vercel.app",
		"https://localhost:5173",
		"https://localhost:8000"
		],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"]
)

from routes import auth_router

app.include_router(auth_router)