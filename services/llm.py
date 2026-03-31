import os
import json
from groq import Groq

def get_client():
    return Groq(api_key=os.getenv('GROQ_API_KEY'))

def extract_search_params(user_query):
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
    client = get_client()
    prompt = f"""You are a music genre expert with deep knowledge of english pop music, electronic music, subgenres, and scenes.

        A user wants music recommendations for: "{user_query}"

        Extract precise search parameters. Be SPECIFIC about subgenres — do not generalise.
        Examples of good specificity:
        - "hard techno" → genres: ["hard techno", "industrial techno", "tekno"], NOT just ["techno", "edm"]
        - "lofi hip hop" → genres: ["lofi hip hop", "chillhop"], NOT just ["hip hop"]
        - "nightclub EDM" → genres: ["edm", "big room house", "electro house"]
        - "jazz cafe" → genres: ["jazz", "smooth jazz", "cafe jazz"]
        - "2010 english pop" → genres: ["english pop", "pop rock", "synthpop"], NOT just ["pop"]

        e.g. "songs that feel like a nightclub" →
        (
            "genres": ["edm", "electronic dance", "house"],
            "mood": "high energy",
            "tempo": "fast",
            "ref_artists": ["Martin Garrix", "Hardwell", "Knock2", "Dimitri Vegas"]
        )
        e.g. "2010 pop vibe" →
        (
            "genres": ["english pop", "pop rock", "synthpop"],
            "mood": "nostalgic",
            "tempo": "medium",
            "ref_artists": ["Taylor Swift", "Lady Gaga", "Katy Perry", "Bruno Mars","Ed Sheeran"]
        )
        e.g. "chill music for working" →
        (
            "genres": ["lofi hip hop", "chillhop", "ambient"],
            "mood": "calm",
            "tempo": "slow",
            "ref_artists": ["Idealism", "Philanthrope", "Nujabes"],
        )
        e.g. "idie pop" →
        (
            "genres": ["indie pop", "indie rock", "alternative"],
            "mood": "upbeat",
            "tempo": "medium",
            "ref_artists": ["Clairo", "Rex Orange County", "Foster", "artic monkeys", "Vampire Weekend"]
        )
        e.g. "tropical house for a summer BBQ" →
        (
            "genres": ["tropical house", "deep house", "chill house"],
            "mood": "happy",
            "tempo": "medium",
            "ref_artists": ["Kygo", "Matoma", "Thomas Jack", "Sam Feldt", "Lost Frequencies"]
        )

        Return ONLY a JSON object with these fields:
        - genres: list of 2-4 (not limited) specific genre/subgenre tags (lowercase, specific)
        - mood: one word describing the mood
        - tempo: one word ("fast", "medium", or "slow")
        - ref_artists: list of 2-3 real artists who are genuinely known for this specific sound

        Return ONLY the JSON, no explanation, no markdown, no backticks.
        """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.3
    )
    print('LLM raw response for search params:', response.choices[0].message.content)  # helpful for debugging
    
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
        - Recently played: {', '.join(taste_profile.get('recently_played', [])[:5])}
        """

    prompt = f"""You are Moodify, an expert music recommendation assistant with deep knowledge of music genres, subgenres, and scenes.

        A user asked for: "{user_query}"

        Their general music taste profile (use this for context, NOT as a constraint):
        {taste_summary}

        IMPORTANT RULES:
        1. The user's REQUEST defines the vibe — this is the top priority. Their taste profile is secondary context only.
        2. If the user asks for hard techno, recommend hard techno. If they ask for jazz, recommend jazz. Do NOT drift toward their usual taste if it contradicts the request.
        3. You are a genre expert. "Hard techno" means artists like Alignment, Truncate, Phase Fatale, Paula Temple — NOT mainstream EDM. "Lofi" means Idealism, Philanthrope — NOT chill pop. Be precise about subgenres.
        4. Evaluate every candidate song critically. If a candidate clearly does not match the requested vibe (wrong tempo, wrong energy, wrong genre), reject it — even if it is popular.
        5. Use your own music knowledge to suggest alternatives if the candidate pool lacks strong matches. Mark these as "source": "llm".
        6. Never recommend a song just because it is popular or because the user has listened to similar artists. It must genuinely fit the vibe.
        7. Do not hallucinate — only suggest real songs by real artists that actually exist.
        8. Aim for 10 songs. You can go as low as 5 if quality demands it. Fewer great picks beats more mediocre ones. Maximum is 20 if the vibe is broad and many candidates fit well.

        Here are candidate songs from Last.fm:
        {candidate_list}

        For each recommendation, write a specific one-sentence reason that mentions concrete musical qualities (tempo, energy, texture, mood) — not vague phrases like "fits the vibe" or "matches the energy".
        Remember to return valid JSON if an artist name like "Axwell/\Ingrosso" causes formatting issues fix it to valid json format.

        Return ONLY a JSON array, no explanation, no markdown:
        [
        {{"name": "Song Name", "artist": "Artist Name", "reason": "specific reason mentioning musical qualities", "source": "lastfm"}},
        {{"name": "Song Name", "artist": "Artist Name", "reason": "specific reason mentioning musical qualities", "source": "llm"}},
        ...
        ]
            """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.5
    )

    raw = response.choices[0].message.content.strip()
    print('LLM raw response for ranked recommendations:', raw)  # helpful for debugging
    return json.loads(raw)