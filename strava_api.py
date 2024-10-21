from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import os
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from blockchain import Blockchain

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

def main():
    # Initialize the blockchain
    blockchain = Blockchain.load_blockchain()

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

    athlete_firstname = athlete_data['firstname']
    athlete_lastname = athlete_data['lastname']
    athlete_measurement = athlete_data['measurement_preference']

    stats_response = session.get(f"https://www.strava.com/api/v3/athletes/{athlete_id}/stats")
    athlete_stats = stats_response.json()

    athlete_ytdride = athlete_stats['ytd_ride_totals']['distance']
    athlete_ytdrun = athlete_stats['ytd_run_totals']['distance']
    athlete_ytdswim = athlete_stats['ytd_swim_totals']['distance']

    athlete_totaldistance = athlete_ytdride + athlete_ytdrun + athlete_ytdswim

    if athlete_measurement == "feet":
        athlete_totaldistance = athlete_totaldistance * 0.3048

    print(f"Total distance moved by {athlete_firstname} {athlete_lastname} is: {athlete_totaldistance} meters")

    # Add the athlete data to the blockchain
    athlete_data = {
        "firstname": athlete_firstname,
        "lastname": athlete_lastname,
        "total_distance": athlete_totaldistance
    }

    blockchain.add_data(json.dumps(athlete_data))

    # Save the updated blockchain
    blockchain.save_blockchain()

    # Print the blockchain
    print("\nBlockchain contents:")
    blockchain.print_chain()

if __name__ == "__main__":
    main()