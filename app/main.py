from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from .strava_auth import StravaAuth
from .blockchain import Blockchain
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")

strava_auth = StravaAuth()
blockchain = Blockchain.load_blockchain()

@app.get("/")
async def root(request: Request):
    leaderboard = blockchain.get_leaderboard()
    leaderboard.sort(key=lambda x: x['total_distance'], reverse=True)
    return templates.TemplateResponse("leaderboard.html", {"request": request, "leaderboard": leaderboard})

@app.get("/authorize")
async def authorize():
    auth_url = strava_auth.get_authorization_url()
    return RedirectResponse(auth_url)

@app.get("/callback")
async def callback(code: str, scope: str):
    try:
        token_data = strava_auth.get_token(code)
        athlete_data = strava_auth.get_athlete_data(token_data)
        
        # Update the athlete data in the blockchain
        blockchain.update_data(athlete_data)
        blockchain.save_blockchain()
        
        return RedirectResponse(url="/")
    except HTTPException as e:
        return {"error": str(e.detail)}