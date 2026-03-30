import os
import json
from groq import Groq

def get_client():
    return Groq(api_key=os.getenv('GROQ_API_KEY'))

def extract_search_params(user_query):
    client = get_client()
    """
    Takes the user's natural language input and extracts
    structured search parameters for Last.fm.
    
    e.g. "songs that feel like a nightclub" →
    {
        "genres": ["edm", "electronic dance", "house"],
        "mood": "high energy",
        "tempo": "fast",
        "ref_artists": ["Martin Garrix", "Hardwell", "Knock2", "Dimitri Vegas"]
    }
    """
    prompt = f"""You are a music expert assistant. A user wants music recommendations.
    
    User's request: "{user_query}"

    Extract search parameters from this request and return ONLY a JSON object with these fields:
    - genres: list of 2-4 music genre/style tags that match (use simple lowercase tags like "edm", "house", "chill", "indie pop")
    - mood: one word describing the mood (e.g. "energetic", "relaxing", "melancholic", "hype")
    - tempo: one word ("fast", "medium", or "slow")  
    - ref_artists: list of 2-3 well known artists that match this vibe

    Return ONLY the JSON, no explanation, no markdown, no backticks."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.7
    )
    
    raw = response.choices[0].message.content.strip()
    return json.loads(raw)


def rank_and_explain(user_query, taste_profile, candidates):
    client = get_client()
    """
    Takes the candidate songs from Last.fm and the user's taste profile,
    then asks the LLM to pick the best matches and explain why.
    
    Returns a list of 8-10 songs with explanations.
    """

    # Format candidates as a simple numbered list for the prompt
    candidate_list = '\n'.join([
        f"{i+1}. {t['name']} by {t['artist']}"
        for i, t in enumerate(candidates[:40])  # cap at 40 to stay within token limits
    ])

    # Format taste profile
    taste_summary = f"""
        - Top artists they love: {', '.join(taste_profile.get('top_artists', [])[:5])}
        - Their top tracks: {', '.join(taste_profile.get('top_tracks', [])[:5])}
    """

    prompt = f"""You are Moodify, an intelligent music recommendation assistant.

                A user asked for: "{user_query}"

                Their music taste profile:
                {taste_summary}

                Here are candidate songs from a music database:
                {candidate_list}

                Your job:
                1. Pick songs from the candidate list that BEST match the user's request AND fit their taste
                2. Use your music knowledge to judge if a song genuinely fits the vibe — don't just match tags blindly
                3. For each pick, write a SHORT one-sentence reason why it fits (be specific about the vibe/energy/mood)
                4. You can pick fewer than 10 if you think only a few are good matches, but try to find at least 5 solid ones. If the candidate list doesn't have enough strong matches, use your own music knowledge to suggest better alternatives that fit the vibe — clearly mark these with "source": "llm" instead of "source": "lastfm"
                5. Never suggest songs that don't exist. Only recommend real, verifiable tracks by real artists.
                6. Consider the user's taste profile when choosing — pick songs that feel like a natural fit for someone with their listening history. But don't be afraid to suggest something outside their usual taste if it fits the vibe well!

                Return ONLY a JSON array, no explanation, no markdown:
                [
                {{"name": "Song Name", "artist": "Artist Name", "reason": "one sentence why it fits", "source": "lastfm"}},
                {{"name": "Song Name", "artist": "Artist Name", "reason": "one sentence why it fits", "source": "llm"}},
                ...
                ]
            """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.7
    )

    raw = response.choices[0].message.content.strip()
    return json.loads(raw)