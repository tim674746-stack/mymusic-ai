from flask import Flask, request, jsonify, render_template_string
import requests
import re
from urllib.parse import quote

app = Flask(__name__)

HTML = r"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#090911">
<title>MyMusic AI Premium</title>

<style>
* { box-sizing: border-box; }

:root {
    --bg: #090911;
    --panel: #141420;
    --purple: #a78bfa;
    --text: #f8f7ff;
    --muted: #a5a3bb;
}

body {
    margin: 0;
    min-height: 100vh;
    font-family: Arial, sans-serif;
    background:
        radial-gradient(ellipse at 10% 0%, #33205a55, transparent 40%),
        radial-gradient(ellipse at 100% 40%, #24265a44, transparent 40%),
        var(--bg);
    color: var(--text);
    padding: 22px 15px 45px;
}

.container {
    width: 100%;
    max-width: 1000px;
    margin: auto;
}

header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 40px;
}

.logo {
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -1px;
}

.logo span { color: var(--purple); }

.badge {
    border: 1px solid #51416d;
    color: #d8c8ff;
    background: #a78bfa18;
    padding: 8px 12px;
    border-radius: 30px;
    font-size: 12px;
}

.hero {
    text-align: center;
    margin: 35px auto 30px;
}

.hero h1 {
    font-size: clamp(34px, 7vw, 60px);
    line-height: 1.08;
    letter-spacing: -2px;
    margin: 0 0 15px;
}

.gradient {
    background: linear-gradient(90deg, #c4b5fd, #f0abfc, #a5b4fc);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.subtitle {
    color: var(--muted);
    line-height: 1.6;
    max-width: 550px;
    margin: auto;
}

.panel {
    max-width: 760px;
    margin: 30px auto;
    padding: 24px;
    background: #141420eF;
    border: 1px solid #ffffff14;
    border-radius: 22px;
    box-shadow: 0 20px 70px #0005;
}

label {
    display: block;
    font-size: 14px;
    font-weight: bold;
    margin: 17px 0 10px;
}

textarea, select {
    width: 100%;
    color: white;
    background: #0b0b14;
    border: 1px solid #343448;
    border-radius: 12px;
    padding: 14px;
    font: inherit;
    outline: none;
}

textarea {
    min-height: 105px;
    resize: vertical;
    line-height: 1.5;
}

textarea:focus, select:focus {
    border-color: var(--purple);
}

select { cursor: pointer; }

button {
    font: inherit;
    font-weight: bold;
    cursor: pointer;
    border: none;
    border-radius: 12px;
    padding: 14px;
    transition: transform .2s, opacity .2s;
}

button:hover {
    transform: translateY(-1px);
    opacity: .9;
}

.main-button {
    width: 100%;
    margin-top: 16px;
    background: linear-gradient(100deg, #c4b5fd, #e9a8ff);
    color: #171024;
}

.voice-button {
    width: 100%;
    margin-top: 10px;
    background: #242337;
    color: white;
    border: 1px solid #49445f;
}

.status {
    text-align: center;
    color: var(--muted);
    font-size: 14px;
    margin: 22px 0;
    line-height: 1.6;
}

.results-heading {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin: 35px 0 17px;
}

.results-heading h2 {
    margin: 0;
    font-size: 22px;
}

.count {
    color: var(--muted);
    font-size: 13px;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
    gap: 17px;
}

.card {
    min-width: 0;
    padding: 13px;
    background: linear-gradient(145deg, #191927, #101019);
    border: 1px solid #ffffff12;
    border-radius: 17px;
    overflow: hidden;
    transition: transform .2s, border-color .2s;
}

.card:hover {
    transform: translateY(-3px);
    border-color: #a78bfa70;
}

.cover {
    width: 100%;
    aspect-ratio: 1;
    object-fit: cover;
    display: block;
    border-radius: 11px;
    background: #27243b;
}

.song-title {
    font-weight: bold;
    font-size: 15px;
    line-height: 1.4;
    margin: 13px 0 5px;
    overflow-wrap: anywhere;
}

.artist {
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 13px;
    overflow-wrap: anywhere;
}

audio {
    width: 100%;
    height: 36px;
    margin-bottom: 8px;
}

.no-preview {
    color: var(--muted);
    font-size: 12px;
    padding: 11px 0;
}

.links {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    margin-top: 9px;
}

.links a {
    text-decoration: none;
    color: #e5ddff;
    background: #a78bfa20;
    border: 1px solid #a78bfa35;
    border-radius: 8px;
    padding: 8px 10px;
    font-size: 12px;
}

.links a:hover { background: #a78bfa38; }

.note {
    text-align: center;
    color: #85839a;
    font-size: 12px;
    line-height: 1.6;
    margin-top: 30px;
}

.hidden { display: none; }

@media (max-width: 500px) {
    body { padding: 16px 12px 35px; }
    .panel { padding: 17px; }
    .hero { margin-top: 28px; }
    .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
    .card { padding: 9px; }
    .song-title { font-size: 13px; }
    .artist { font-size: 12px; }
    .badge { font-size: 10px; }
}
</style>
</head>

<body>
<div class="container">

<header>
    <div class="logo">🎧 MyMusic <span>AI</span></div>
    <div class="badge">✦ PREMIUM DESIGN</div>
</header>

<section class="hero">
    <h1>Ta musique.<br><span class="gradient">Ton univers.</span></h1>
    <p class="subtitle">
        Décris tes envies musicales et découvre des morceaux,
        leurs pochettes et les extraits disponibles.
    </p>
</section>

<section class="panel">
    <label for="theme">🎵 Quelle musique recherches-tu ?</label>
    <textarea id="theme"
        placeholder="Ex. : 15 sons de Gazo avec des collaborations..."></textarea>

    <button class="voice-button" id="voice" onclick="speakTheme()">
        🎤 Parler à mon IA
    </button>

    <label for="platform">🎧 Où veux-tu écouter ta musique ?</label>
    <select id="platform">
        <option value="spotify">Spotify</option>
        <option value="apple_music">Apple Music</option>
        <option value="youtube_music">YouTube Music</option>
        <option value="deezer">Deezer</option>
        <option value="amazon_music">Amazon Music</option>
    </select>

    <button class="main-button" id="searchButton" onclick="generatePlaylist()">
        ✨ Découvrir ma sélection
    </button>
</section>

<div id="status" class="status" aria-live="polite">
    Ton espace musical est prêt. 🎶
</div>

<section id="resultsSection" class="hidden">
    <div class="results-heading">
        <h2>Ta sélection ✨</h2>
        <span class="count" id="count"></span>
    </div>
    <div class="grid" id="results"></div>
</section>

<p class="note">
    Les résultats proviennent du catalogue Apple.<br>
    Certains morceaux proposent un extrait audio. Les liens ouvrent
    une recherche sur la plateforme choisie ; aucun compte musical
    n'est modifié et aucune playlist n'est créée automatiquement.
</p>

</div>

<script>
function speakTheme() {
    const Recognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!Recognition) {
        alert("Essaie Chrome ou Edge pour utiliser la reconnaissance vocale.");
        return;
    }

    const recognition = new Recognition();
    const button = document.getElementById("voice");

    recognition.lang = "fr-FR";
    recognition.interimResults = false;

    recognition.onstart = () => {
        button.textContent = "🎤 Je t'écoute...";
        button.disabled = true;
    };

    recognition.onresult = event => {
        document.getElementById("theme").value =
            event.results[0][0].transcript;
    };

    recognition.onerror = () => {
        alert("Vérifie l'autorisation du micro dans ton navigateur.");
    };

    recognition.onend = () => {
        button.textContent = "🎤 Parler à mon IA";
        button.disabled = false;
    };

    recognition.start();
}

function platformSearch(platform, title, artist) {
    const query = encodeURIComponent(title + " " + artist);

    const urls = {
        spotify: "https://open.spotify.com/search/" + query,
        apple_music: "https://music.apple.com/fr/search?term=" + query,
        youtube_music: "https://music.youtube.com/search?q=" + query,
        deezer: "https://www.deezer.com/search/" + query,
        amazon_music: "https://music.amazon.fr/search/" + query
    };

    return urls[platform] || urls.spotify;
}

function createCard(song, platform) {
    const card = document.createElement("article");
    card.className = "card";

    const cover = document.createElement("img");
    cover.className = "cover";
    cover.alt = "Pochette de " + song.title;
    cover.loading = "lazy";
    cover.src = song.cover || "";
    cover.onerror = () => {
        cover.onerror = null;
        cover.src = "https://placehold.co/400x400/19192d/c4b5fd?text=MyMusic";
    };
    card.appendChild(cover);

    const title = document.createElement("div");
    title.className = "song-title";
    title.textContent = song.title;
    card.appendChild(title);

    const artist = document.createElement("div");
    artist.className = "artist";
    artist.textContent = song.artist;
    card.appendChild(artist);

    if (song.preview) {
        const audio = document.createElement("audio");
        audio.controls = true;
        audio.preload = "none";
        audio.src = song.preview;
        audio.setAttribute("aria-label", "Extrait de " + song.title);
        card.appendChild(audio);
    } else {
        const unavailable = document.createElement("div");
        unavailable.className = "no-preview";
        unavailable.textContent = "Extrait non disponible";
        card.appendChild(unavailable);
    }

    const links = document.createElement("div");
    links.className = "links";

    const searchLink = document.createElement("a");
    searchLink.href = platformSearch(platform, song.title, song.artist);
    searchLink.target = "_blank";
    searchLink.rel = "noopener noreferrer";
    searchLink.textContent = "Écouter ↗";
    links.appendChild(searchLink);

    if (song.appleLink) {
        const appleLink = document.createElement("a");
        appleLink.href = song.appleLink;
        appleLink.target = "_blank";
        appleLink.rel = "noopener noreferrer";
        appleLink.textContent = "Catalogue Apple";
        links.appendChild(appleLink);
    }

    card.appendChild(links);
    return card;
}

async function generatePlaylist() {
    const theme = document.getElementById("theme").value.trim();
    const platform = document.getElementById("platform").value;
    const status = document.getElementById("status");
    const results = document.getElementById("results");
    const section = document.getElementById("resultsSection");
    const button = document.getElementById("searchButton");

    if (!theme) {
        status.textContent = "Décris d'abord la playlist que tu souhaites.";
        return;
    }

    button.disabled = true;
    button.textContent = "🔎 Recherche en cours...";
    status.textContent = "🔎 Recherche des morceaux et de leurs pochettes...";
    results.replaceChildren();
    section.classList.add("hidden");

    try {
        const response = await fetch("/generate", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({theme, platform})
        });

        const data = await response.json();

        if (!response.ok) {
            status.textContent = data.message || "Une erreur est survenue.";
            return;
        }

        if (!data.songs || data.songs.length === 0) {
            status.textContent = data.message || "Aucun morceau trouvé.";
            return;
        }

        data.songs.forEach(song => {
            results.appendChild(createCard(song, platform));
        });

        document.getElementById("count").textContent =
            data.songs.length + " morceau(x)";
        section.classList.remove("hidden");
        status.textContent = data.message || "Voici ta sélection musicale ! 🎧";

    } catch (error) {
        status.textContent =
            "Impossible de contacter le serveur. Réessaie dans quelques instants.";
    } finally {
        button.disabled = false;
        button.textContent = "✨ Découvrir ma sélection";
    }
}
</script>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    theme = str(data.get("theme", "")).strip()
    platform = str(data.get("platform", "")).strip()

    platforms = {
        "spotify": "Spotify",
        "apple_music": "Apple Music",
        "youtube_music": "YouTube Music",
        "deezer": "Deezer",
        "amazon_music": "Amazon Music",
    }

    if not theme:
        return jsonify({"message": "Décris la playlist que tu veux."}), 400

    if platform not in platforms:
        return jsonify({"message": "Plateforme non reconnue."}), 400

    match = re.search(
        r"\b(\d{1,2})\s*(?:sons?|morceaux?|titres?)\b",
        theme.lower()
    )
    nombre = min(int(match.group(1)), 50) if match else 20

    artist_match = re.search(
        r"\b(?:de|du|des|d['’])\s*"
        r"([a-zA-ZÀ-ÿ0-9][a-zA-ZÀ-ÿ0-9 '&-]*)",
        theme,
        re.IGNORECASE
    )

    recherche = artist_match.group(1).strip() if artist_match else theme

    recherche = re.split(
        r"\b(?:avec|pour|dans|qui|triste|mélodieux)\b",
        recherche,
        maxsplit=1,
        flags=re.IGNORECASE
    )[0].strip(" .,!?")

    if not recherche:
        recherche = theme

    try:
        response = requests.get(
            "https://itunes.apple.com/search",
            params={
                "term": recherche,
                "entity": "song",
                "limit": 200,
                "country": "FR"
            },
            timeout=20
        )
        response.raise_for_status()
        results = response.json().get("results", [])

        if not results:
            return jsonify({
                "message": "Aucun morceau trouvé. Essaie un autre artiste."
            })

        artist_lower = recherche.lower()

        def score(song):
            artist = song.get("artistName", "").lower()
            title = song.get("trackName", "").lower()
            value = 0
            if artist_lower in artist:
                value += 3
            if artist_lower in title:
                value += 1
            return value

        results.sort(key=score, reverse=True)

        songs = []
        seen = set()

        for song in results:
            title = (song.get("trackName") or "").strip()
            artist = (song.get("artistName") or "").strip()
            key = (title.casefold(), artist.casefold())

            if not title or not artist or key in seen:
                continue

            seen.add(key)

            cover = song.get("artworkUrl100", "")
            if cover:
                cover = cover.replace("100x100", "600x600")

            songs.append({
                "title": title,
                "artist": artist,
                "cover": cover,
                "preview": song.get("previewUrl", ""),
                "appleLink": song.get("trackViewUrl", "")
            })

            if len(songs) >= nombre:
                break

        if not songs:
            return jsonify({
                "message": "Aucun morceau exploitable. Essaie une autre recherche."
            })

        return jsonify({
            "message": (
                f"🎧 Sélection trouvée pour : {recherche}. "
                f"Plateforme choisie : {platforms[platform]}. "
                "Les résultats viennent du catalogue Apple."
            ),
            "songs": songs
        })

    except requests.RequestException:
        return jsonify({
            "message": (
                "Impossible de contacter le catalogue musical. "
                "Réessaie dans quelques instants."
            )
        }), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
