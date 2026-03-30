import os
import spotipy

def build_taste_profile(sp):
    """
    Builds a personalised taste profile from the user's Spotify data.
    sp = an authenticated Spotipy client
    """
    profile = {}

    # Top artists (medium term = last ~6 months)
    top_artists_data = sp.current_user_top_artists(limit=10, time_range='medium_term')
    profile['top_artists'] = [a['name'] for a in top_artists_data['items']]

    # Top tracks
    top_tracks_data = sp.current_user_top_tracks(limit=10, time_range='medium_term')
    profile['top_tracks'] = [
        f"{t['name']} by {t['artists'][0]['name']}"
        for t in top_tracks_data['items']
    ]

    return profile