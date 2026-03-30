import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from flask import Flask, redirect, request, session, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')
app.secret_key = os.getenv('SECRET_KEY')

# Spotify scopes — permissions asking from user
SCOPE = 'user-top-read user-library-read playlist-modify-public playlist-modify-private'

def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
        scope=SCOPE
    )

def get_spotify_client():
    token_info = session.get('token_info')
    if not token_info:
        return None
    # Auto-refresh token if expired
    sp_oauth = get_spotify_oauth()
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        session['token_info'] = token_info
    return spotipy.Spotify(auth=token_info['access_token'])

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/login')
def login():
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp_oauth = get_spotify_oauth()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect('/')

@app.route('/me')
def me():
    sp = get_spotify_client()
    if not sp:
        return jsonify({'error': 'not logged in'}), 401
    user = sp.current_user()
    top_tracks = sp.current_user_top_tracks(limit=15, time_range='medium_term')
    return jsonify({
        'name': user['display_name'],
        'top_tracks': [t['name'] + ' — ' + t['artists'][0]['name'] 
                       for t in top_tracks['items']]
    })

if __name__ == '__main__':
    app.run(debug=True)