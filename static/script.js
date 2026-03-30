let currentRecommendations = [];
let currentQuery = '';

// ── On page load: check if user is logged in ──
async function init() {
  try {
    const res = await fetch('/me');
    if (res.status === 401) {
      showLogin();
      return;
    }
    const data = await res.json();
    document.getElementById('userName').textContent = data.name;
    showApp();
  } catch {
    showLogin();
  }
}

function showLogin() {
  document.getElementById('loginScreen').style.display = 'flex';
  document.getElementById('mainApp').style.display = 'none';
}

function showApp() {
  document.getElementById('loginScreen').style.display = 'none';
  document.getElementById('mainApp').style.display = 'block';
}

// ── Search ──
function setQuery(text) {
  document.getElementById('queryInput').value = text;
  search();
}

async function search() {
  const query = document.getElementById('queryInput').value.trim();
  if (!query) return;

  currentQuery = query;
  currentRecommendations = [];

  // UI state: loading
  document.getElementById('searchBtn').disabled = true;
  document.getElementById('searchBtn').textContent = 'Finding...';
  document.getElementById('status').classList.add('visible');
  document.getElementById('results').classList.remove('visible');
  document.getElementById('vibeSummary').classList.remove('visible');
  document.getElementById('statusText').textContent = 'Analysing your vibe';

  try {
    const res = await fetch('/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });

    const data = await res.json();

    if (data.error) {
      showToast('Something went wrong — try again');
      return;
    }

    currentRecommendations = data.recommendations;
    renderVibeSummary(data.search_params);
    renderSongs(data.recommendations, query);

  } catch (err) {
    showToast('Connection error — is the server running?');
  } finally {
    document.getElementById('searchBtn').disabled = false;
    document.getElementById('searchBtn').textContent = 'Find songs';
    document.getElementById('status').classList.remove('visible');
  }
}

// ── Render vibe tags ──
function renderVibeSummary(params) {
  const container = document.getElementById('vibeTags');
  container.innerHTML = '<span class="vibe-label">Moodify heard:</span>';

  const tags = [
    ...(params.genres || []),
    params.mood,
    params.tempo ? params.tempo + ' tempo' : null
  ].filter(Boolean);

  tags.forEach(tag => {
    const el = document.createElement('span');
    el.className = 'vibe-tag';
    el.textContent = tag;
    container.appendChild(el);
  });

  document.getElementById('vibeSummary').classList.add('visible');
}

// ── Render song cards ──
function renderSongs(songs, query) {
  const list = document.getElementById('songList');
  list.innerHTML = '';

  songs.forEach((song, i) => {
    const sourceClass = song.source === 'llm' ? 'source-llm' : 'source-lastfm';
    const sourceLabel = song.source === 'llm' ? 'Moodify pick' : 'Last.fm';

    const card = document.createElement('div');
    card.className = 'song-card';
    card.innerHTML = `
      <span class="song-num">${i + 1}</span>
      <div class="song-info">
        <div class="song-name">${song.name}</div>
        <div class="song-artist">${song.artist}</div>
        <div class="song-reason">${song.reason}</div>
      </div>
      <span class="song-source ${sourceClass}">${sourceLabel}</span>
    `;
    list.appendChild(card);
  });

  document.getElementById('resultsTitle').textContent =
    `${songs.length} songs for "${query}"`;
  document.getElementById('results').classList.add('visible');
}

// ── Save playlist ──
async function savePlaylist() {
  if (!currentRecommendations.length) return;

  const btn = document.getElementById('saveBtn');
  btn.disabled = true;
  btn.textContent = 'Saving...';

  try {
    const res = await fetch('/save-playlist', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: currentQuery,
        songs: currentRecommendations
      })
    });

    const data = await res.json();

    if (data.success) {
      showToast('Playlist saved to Spotify!');
      btn.textContent = 'Saved!';
    } else {
      showToast('Could not save — try again');
      btn.disabled = false;
      btn.textContent = 'Save to Spotify';
    }
  } catch {
    showToast('Connection error');
    btn.disabled = false;
    btn.textContent = 'Save to Spotify';
  }
}

// ── Enter key to search ──
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('queryInput').addEventListener('keydown', e => {
    if (e.key === 'Enter') search();
  });
  init();
});

// ── Toast ──
function showToast(msg) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3000);
}
