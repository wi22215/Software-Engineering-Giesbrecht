from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import requests

# Lade Umgebungsvariablen aus der .env-Datei
load_dotenv()

# Instagram API Konfiguration
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID")
INSTAGRAM_API_URL = "https://graph.facebook.com/v17.0"

# Initialisiere Flask
app = Flask(__name__)

# Sicherstellen, dass der Upload-Ordner existiert
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Route: Startseite
@app.route('/')
def home():
    return render_template('index.html')

# Route: Datei-Upload
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    caption = request.form['caption']

    if not file:
        return jsonify({"error": "No file provided"}), 400

    # Speichere die Datei im Upload-Ordner
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Optional: Auf Instagram hochladen
    try:
        response = upload_to_instagram(file_path, caption)
        return jsonify({"message": "File uploaded successfully to Instagram", "response": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Funktion: Hochladen auf Instagram
def upload_to_instagram(file_path, caption):
    # Schritt 1: Medienobjekt erstellen
    media_url = f"{INSTAGRAM_API_URL}/{INSTAGRAM_USER_ID}/media"
    media_payload = {
        "image_url": file_path,  # Für Bilder (oder video_url für Videos)
        "caption": caption,
        "access_token": INSTAGRAM_ACCESS_TOKEN,
    }

    media_response = requests.post(media_url, data=media_payload)
    if media_response.status_code != 200:
        raise Exception(f"Instagram API Error: {media_response.text}")

    media_id = media_response.json().get("id")

    # Schritt 2: Medienobjekt veröffentlichen
    publish_url = f"{INSTAGRAM_API_URL}/{INSTAGRAM_USER_ID}/media_publish"
    publish_payload = {
        "creation_id": media_id,
        "access_token": INSTAGRAM_ACCESS_TOKEN,
    }

    publish_response = requests.post(publish_url, data=publish_payload)
    if publish_response.status_code != 200:
        raise Exception(f"Instagram API Error: {publish_response.text}")

    return publish_response.json()

# Route: Server-Health-Check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "Server is running"}), 200

if __name__ == "__main__":
    app.run(debug=True)
