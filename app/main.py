from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .strava_auth import StravaAuth
from .blockchain import Blockchain
import json

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

strava_auth = StravaAuth()
blockchain = Blockchain.load_blockchain()

@app.get("/api/leaderboard")
async def get_leaderboard():
    leaderboard = blockchain.get_leaderboard()
    leaderboard.sort(key=lambda x: x['total_distance'], reverse=True)
    return JSONResponse(content=leaderboard)

@app.get("/api/authorize")
async def authorize():
    auth_url = strava_auth.get_authorization_url()
    return JSONResponse(content={"auth_url": auth_url})

@app.get("/api/callback")
async def callback(code: str, scope: str):
    try:
        token_data = strava_auth.get_token(code)
        athlete_data = strava_auth.get_athlete_data(token_data)
        
        # Update the athlete data in the blockchain
        blockchain.update_data(athlete_data)
        blockchain.save_blockchain()
        
        return JSONResponse(content={"success": True})
    except HTTPException as e:
        return JSONResponse(content={"error": str(e.detail)})