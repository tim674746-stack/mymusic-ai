
from flask import Flask, request, jsonify, render_template_string
import requests
import re

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MyMusic AI</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            min-height: 100vh;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #101020, #202044);
            color: white;
            padding: 25px 15px;
        }
        .container {
            max-width: 700px;
            margin: 35px auto;
            background: #19192d;
            border: 1px solid #383852;
            border-radius: 22px;
            padding: 28px;
            box-shadow: 0 15px 50px #0005;
        }
        h1 { text-align: center; font-size: 32px; }
        .subtitle {
            text-align: center;
            color: #b9b9d0;
            margin-bottom: 30px;
        }
        label {
            display: block;
            margin: 20px 0 9px;
            font-weight: bold;
        }
        textarea, select {
            width: 100%;
            border: 1px solid #464665;
            background: #101020;
            color: white;
            border-radius: 12px;
            padding: 14px;
            font-size: 16px;
        }
        textarea { min-height: 115px; resize: vertical; }
        button {
            width: 100%;
            border: 0;
            border-radius: 12px;
            padding: 15px;
            margin-top: 15px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }
        .main-button { background: #a78bfa; color: #171329; }
        .voice-button {
            background: #292943;
            color: white;
            border: 1px solid #555575;
        }
        button:hover { opacity: 0.88; }
        #result {
            margin-top: 22px;
            padding: 15px;
            background: #101020;
            border-radius: 12px;
            line-height: 1.6;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
        }
        .note {
            margin-top: 22px;
            color: #a5a5bd;
            font-size: 13px;
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <main class="container">
        <h1>🎧 MyMusic AI</h1>
        <p class="subtitle">Ta musique. Ton humeur. Ta playlist.</p>

        <label for="theme">Quelle playlist veux-tu ?</label>
        <textarea id="theme"
            placeholder="Ex. : 10 sons de Gazo, avec ses collaborations..."></textarea>

        <button class="voice-button" id="voice" onclick="speakTheme()">
            🎤 Parler à mon IA
        </button>

        <label for="platform">Choisis ta plateforme</label>
        <select id="platform">
            <option value="spotify">Spotify</option>
            <option value="apple_music">Apple Music</option>
            <option value="youtube_music">YouTube Music</option>
            <option value="deezer">Deezer</option>
            <option value="amazon_music">Amazon Music</option>
        </select>

        <button class="main-button" onclick="generatePlaylist()">
            ✨ Préparer ma playlist
        </button>

        <div id="result">
            Ton espace musical est prêt. Décris la playlist de tes rêves !
        </div>

        <p class="note">
            Les morceaux sont recherchés dans le catalogue Apple.
            Cette version ne crée pas encore de playlist sur ton compte.
        </p>
    </main>

    <script>
        function speakTheme() {
            const Recognition =
                window.SpeechRecognition || window.webkitSpeechRecognition;

            if (!Recognition) {
                alert("Essaie Microsoft Edge ou Google Chrome pour utiliser le micro.");
                return;
            }

            const recognition = new Recognition();
            recognition.lang = "fr-FR";
            recognition.interimResults = false;

            recognition.onstart = () => {
                document.getElementById("voice").textContent = "🎤 Je t'écoute...";
            };

            recognition.onresult = (event) => {
                document.getElementById("theme").value =
                    event.results[0][0].transcript;
            };

            recognition.onerror = () => {
                alert("Vérifie l'autorisation du micro dans ton navigateur.");
            };

            recognition.onend = () => {
                document.getElementById("voice").textContent = "🎤 Parler à mon IA";
            };

            recognition.start();
        }

        async function generatePlaylist() {
            const theme = document.getElementById("theme").value.trim();
            const platform = document.getElementById("platform").value;
            const result = document.getElementById("result");

            if (!theme) {
                result.textContent = "Décris d'abord la playlist que tu souhaites.";
                return;
            }

            result.textContent = "🔎 Recherche des morceaux...";

            try {
                const response = await fetch("/generate", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({theme, platform})
                });

                const data = await response.json();
                result.textContent = data.message || "Aucun résultat.";
            } catch (error) {
                result.textContent =
                    "Impossible de contacter le serveur. Vérifie qu'il est démarré.";
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

    # Repère un artiste après "de", "du" ou "d'"
    artist_match = re.search(
        r"\b(?:de|du|des|d['’])\s*([a-zA-ZÀ-ÿ0-9][a-zA-ZÀ-ÿ0-9 '&-]*)",
        theme,
        re.IGNORECASE
    )

    recherche = artist_match.group(1).strip() if artist_match else theme
    recherche = re.split(
        r"\b(?:avec|pour|et|dans|qui|triste|mélodieux)\b",
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
                "message": "Aucun morceau trouvé. Essaie avec un nom d'artiste."
            })

        songs = []
        seen = set()

        # Favorise les titres où l'artiste recherché apparaît,
        # tout en gardant les collaborations.
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

        for song in results:
            title = song.get("trackName", "").strip()
            artist = song.get("artistName", "").strip()
            key = (title.casefold(), artist.casefold())

            if title and artist and key not in seen:
                seen.add(key)
                songs.append(f"🎵 {title} — {artist}")

            if len(songs) >= nombre:
                break

        if not songs:
            message = "Aucun morceau exploitable trouvé. Essaie une autre recherche."
        else:
            message = (
                f"🎧 MyMusic AI\n"
                f"Plateforme choisie : {platforms[platform]}\n"
                f"Recherche : {recherche}\n\n"
                f"Voici les morceaux trouvés :\n\n"
                + "\n".join(songs)
                + "\n\nℹ️ Résultats du catalogue Apple. "
                "Les collaborations peuvent apparaître. "
                "La playlist n'est pas encore créée sur ton compte."
            )

        return jsonify({"message": message})

    except requests.RequestException:
        return jsonify({
            "message": "Impossible de contacter le catalogue Apple. Vérifie ta connexion Internet."
        }), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

