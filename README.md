# Moodify :musical_note:
Welcome to moodify, everybody :wave: ! Here is the destination where you convert your current mood into a playlist! Describe a vibe, place, feeling, or activity, and Moodify helps you find the perfect soundtrack.
## What it does
By typing things like:
- *"high energy EDM festival"*
- *"late night drive alone"*
- *"relaxing Sunday morning coffee"*
- *"pregame hype before going out"*

Moodify interprets requests using an LLM specifically [Groq](https://groq.com/), searches for tracks on [LastFM](https://www.last.fm/home), cross-references it with your personal Spotify listening history, and then the LLM chooses the most suitable music that best describes the vibe from LastFM. Last but not least, save it to your real Spotify account!


---

## How it works
```
User types a vibe
        ↓
LLM extracts genres, mood, tempo, reference artists
        ↓
Last.fm API searches for real verified tracks matching those tags
        ↓
Last.fm API searches top tracks for reference artists
        ↓
Spotify API fetches user's top artists, top tracks, recently played
        ↓
LLM re-ranks candidates against user taste profile + fills gaps with own knowledge
        ↓
Results shown with source badge (Last.fm discovered / Moodify pick) **Moodify pick == LLM pick**
        ↓
One tap saves as a Spotify playlist
```

The LLM runs twice — once to *understand* the request, once to *select* music that matches the user's query. Understand the request by generating genre tags. As a result, tracks with the genre tag are picked up, but only the music that matches the user query is chosen.

---

---

## Tech stack
| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Spotify integration | Spotipy (OAuth 2.0) |
| Music database | Last.fm API |
| AI / LLM | Llama 3.3 70B via Groq API |
| Frontend | Vanilla HTML, CSS, JavaScript |
| Deployment | Render |

---

## Project structure
```
moodify/
├── app.py              # Flask app — all routes
├── services/
│   ├── spotify.py      # Spotify OAuth + taste profile builder
│   ├── lastfm.py       # Last.fm tag search + candidate pool builder
│   └── llm.py          # Groq/LLama prompts — vibe extraction + ranking
├── static/             
│   └── index.html      # Frontend
|   └── script.js       # Frontend logic + backend communication
|   └── style.css       # Frontend
├── .env                # Secret keys (never committed)
└── requirements.txt
```

---
## Running locally
> [!NOTE]
> Due to limitations in the Spotify API, users can't authenticate with Moodify unless I add them manually. Therefore, the user needs to run it locally if they want to use the web app. A Spotify Premium Account is required to use the Spotify API (which is frustrating). Trying to fix the limitation by providing a continue as a guest option for the user.

**Prerequisites:** Python 3.10+, a Spotify Premium account.

```bash
# Clone and set up
git clone https://github.com/NCCHANG/moodify
cd moodify
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file with the following contents on .env variable section. 

## .env variable
```
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
LASTFM_API_KEY=your_lastfm_api_key
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=any_random_string
```

**Getting API keys:**
- Spotify — [developer.spotify.com](https://developer.spotify.com) → create app, set redirect URI to `http://127.0.0.1:5000/callback`
- Last.fm — [last.fm/api/account/create](https://www.last.fm/api/account/create) (instant, free)
- Groq — [console.groq.com](https://console.groq.com) (free tier, no credit card)

---

## To visit the site
[moodify-n571.onrender.com](https://moodify-n571.onrender.com)

*Note: Runs on Render free tier — may take 30–60 seconds to wake up on first visit.*
