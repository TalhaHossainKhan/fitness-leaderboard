from requests_oauthlib import OAuth2Session
import os
from dotenv import load_dotenv
import requests
from fastapi import HTTPException

load_dotenv()

class StravaAuth:
    def __init__(self):
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.redirect_url = os.getenv('REDIRECT_URL', 'http://localhost:8000/callback')
        self.scope = "activity:read_all,profile:read_all"
        self.auth_base_url = "https://www.strava.com/oauth/authorize"
        self.token_url = "https://www.strava.com/api/v3/oauth/token"

    def get_authorization_url(self):
        oauth = OAuth2Session(client_id=self.client_id, redirect_uri=self.redirect_url, scope=self.scope)
        authorization_url, _ = oauth.authorization_url(self.auth_base_url)
        return authorization_url

    def get_token(self, code):
        try:
            payload = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'grant_type': 'authorization_code'
            }
            response = requests.post(self.token_url, data=payload)
            response.raise_for_status()
            token_data = response.json()
            
            if 'access_token' not in token_data:
                raise HTTPException(status_code=400, detail="Access token not found in Strava response")
            
            return token_data
        except requests.RequestException as e:
            raise HTTPException(status_code=400, detail=f"Error exchanging token: {str(e)}")

    def get_athlete_data(self, token):
        oauth = OAuth2Session(client_id=self.client_id, token=token)
        
        try:
            athlete_response = oauth.get("https://www.strava.com/api/v3/athlete")
            athlete_response.raise_for_status()
            athlete_data = athlete_response.json()
            athlete_id = athlete_data['id']

            stats_response = oauth.get(f"https://www.strava.com/api/v3/athletes/{athlete_id}/stats")
            stats_response.raise_for_status()
            athlete_stats = stats_response.json()

            athlete_ytdride = athlete_stats.get('ytd_ride_totals', {}).get('distance', 0)
            athlete_ytdrun = athlete_stats.get('ytd_run_totals', {}).get('distance', 0)
            athlete_ytdswim = athlete_stats.get('ytd_swim_totals', {}).get('distance', 0)

            athlete_totaldistance = athlete_ytdride + athlete_ytdrun + athlete_ytdswim

            # Use a default value if 'measurement_preference' is not present
            measurement_preference = athlete_data.get('measurement_preference', 'meters')

            if measurement_preference == "feet":
                athlete_totaldistance = athlete_totaldistance * 0.3048

            return {
                "id": athlete_id,
                "firstname": athlete_data.get('firstname', ''),
                "lastname": athlete_data.get('lastname', ''),
                "total_distance": athlete_totaldistance,
                "measurement_preference": measurement_preference
            }
        except requests.RequestException as e:
            raise HTTPException(status_code=400, detail=f"Error fetching athlete data: {str(e)}")
