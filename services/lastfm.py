import os
import requests

LASTFM_BASE = 'http://ws.audioscrobbler.com/2.0/'

def get_api_key():
    return os.getenv('LASTFM_API_KEY')

def search_by_tag(tag, limit=20):
    """
    Get top tracks for a given tag/genre from Last.fm
    e.g. tag = "progressive house" → returns list of tracks
    """
    params = {
        'method': 'tag.getTopTracks',
        'tag': tag,
        'api_key': get_api_key(),
        'format': 'json',
        'limit': limit
    }
    response = requests.get(LASTFM_BASE, params=params)
    data = response.json()

    tracks = []
    if 'tracks' in data and 'track' in data['tracks']:
        for t in data['tracks']['track']:
            tracks.append({
                'name': t['name'],
                'artist': t['artist']['name']
            })
    return tracks

def get_similar_artists(artist_name, limit=5):
    """
    Get artists similar to a given artist
    e.g. "Martin Garrix" → ["Tiesto", "Hardwell", "Avicii", ...]
    """
    params = {
        'method': 'artist.getSimilar',
        'artist': artist_name,
        'api_key': get_api_key(),
        'format': 'json',
        'limit': limit
    }
    response = requests.get(LASTFM_BASE, params=params)
    data = response.json()

    artists = []
    if 'similarartists' in data and 'artist' in data['similarartists']:
        for a in data['similarartists']['artist']:
            artists.append(a['name'])
    return artists

def get_artist_top_tracks(artist_name, limit=5):
    """
    Get top tracks from a specific artist
    """
    params = {
        'method': 'artist.getTopTracks',
        'artist': artist_name,
        'api_key': get_api_key(),
        'format': 'json',
        'limit': limit
    }
    response = requests.get(LASTFM_BASE, params=params)
    data = response.json()

    tracks = []
    if 'toptracks' in data and 'track' in data['toptracks']:
        for t in data['toptracks']['track']:
            tracks.append({
                'name': t['name'],
                'artist': artist_name
            })
    return tracks

def build_candidate_pool(genres, ref_artists, limit_per_source=15):
    """
    Combines tag search + similar artist discovery into one
    big candidate pool of songs to pass to the LLM.
    
    genres      = list of genre/mood tags e.g. ["edm", "progressive house"]
    ref_artists = list of artist names e.g. ["Martin Garrix", "Kygo"]
    """
    candidates = []
    seen = set()  # avoid duplicates

    # 1. Search by each genre tag
    for genre in genres[:3]:  # limit to top 3 to avoid too many API calls
        tracks = search_by_tag(genre, limit=limit_per_source)
        for t in tracks:
            key = f"{t['name']}|{t['artist']}".lower()
            if key not in seen:
                seen.add(key)
                candidates.append(t)

    # 2. Get similar artists and their top tracks
    for artist in ref_artists[:3]:
        similar = get_similar_artists(artist, limit=4)
        for similar_artist in similar:
            tracks = get_artist_top_tracks(similar_artist, limit=3)
            for t in tracks:
                key = f"{t['name']}|{t['artist']}".lower()
                if key not in seen:
                    seen.add(key)
                    candidates.append(t)

    return candidates