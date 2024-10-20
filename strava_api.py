from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import os
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' 

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
redirect_url = "http://localhost:8000/callback"

scope = "profile:read_all,activity:read_all,read_all"

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.server.path = self.path
        self.wfile.write(b"Authentication successful. You can close this window.")

def get_auth_response():
    server = HTTPServer(('localhost', 8000), CallbackHandler)
    server.handle_request()
    return server.path

session = OAuth2Session(client_id=client_id, redirect_uri=redirect_url, scope=scope)

auth_base_url = "https://www.strava.com/oauth/authorize"
auth_link, _ = session.authorization_url(auth_base_url)

webbrowser.open(auth_link)

redirect_response = get_auth_response()

token_url = "https://www.strava.com/api/v3/oauth/token"
session.fetch_token(
    token_url=token_url,
    client_id=client_id,
    client_secret=client_secret,
    authorization_response=redirect_response,
    include_client_id=True
)

athlete_response = session.get("https://www.strava.com/api/v3/athlete")
athlete_data = athlete_response.json()
athlete_id = athlete_data['id']

stats_response = session.get(f"https://www.strava.com/api/v3/athletes/{athlete_id}/stats")

print("\nAthlete Profile:")
print(json.dumps(athlete_data, indent=2))

print("\nAthlete Stats:")
print(json.dumps(stats_response.json(), indent=2))