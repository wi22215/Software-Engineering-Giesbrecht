from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

app = Flask(__name__)

# Instagram API-Konfiguration
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID")
INSTAGRAM_API_URL = "https://graph.facebook.com/v17.0"

# Route für die Startseite
@app.route('/')
def home():
    return "Welcome to the Instagram Uploader!"

# Route: Testen der Verbindung
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "Backend is running"}), 200

# Route: Bild-Upload
@app.route('/upload/image', methods=['POST'])
def upload_image():
    data = request.json
    image_url = data.get("image_url")
    caption = data.get("caption")

    if not image_url or not caption:
        return jsonify({"error": "Missing required fields: image_url or caption"}), 400

    # API-Aufruf zur Veröffentlichung eines Bildes
    url = f"{INSTAGRAM_API_URL}/{INSTAGRAM_USER_ID}/media"
    payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": INSTAGRAM_ACCESS_TOKEN
    }

    response = requests.post(url, data=payload)
    if response.status_code == 200:
        media_id = response.json().get("id")

        # Veröffentlichung des Beitrags
        publish_url = f"{INSTAGRAM_API_URL}/{INSTAGRAM_USER_ID}/media_publish"
        publish_payload = {"creation_id": media_id, "access_token": INSTAGRAM_ACCESS_TOKEN}
        publish_response = requests.post(publish_url, data=publish_payload)

        if publish_response.status_code == 200:
            return jsonify({"message": "Image uploaded successfully"}), 200
        else:
            return jsonify({"error": "Failed to publish media"}), 500
    else:
        return jsonify({"error": "Failed to upload media"}), 500

# Route: Video-Upload
@app.route('/upload/video', methods=['POST'])
def upload_video():
    data = request.json
    video_url = data.get("video_url")
    caption = data.get("caption")

    if not video_url or not caption:
        return jsonify({"error": "Missing required fields: video_url or caption"}), 400

    # API-Aufruf zur Veröffentlichung eines Videos
    url = f"{INSTAGRAM_API_URL}/{INSTAGRAM_USER_ID}/media"
    payload = {
        "video_url": video_url,
        "caption": caption,
        "access_token": INSTAGRAM_ACCESS_TOKEN
    }

    response = requests.post(url, data=payload)
    if response.status_code == 200:
        media_id = response.json().get("id")

        # Veröffentlichung des Beitrags
        publish_url = f"{INSTAGRAM_API_URL}/{INSTAGRAM_USER_ID}/media_publish"
        publish_payload = {"creation_id": media_id, "access_token": INSTAGRAM_ACCESS_TOKEN}
        publish_response = requests.post(publish_url, data=publish_payload)

        if publish_response.status_code == 200:
            return jsonify({"message": "Video uploaded successfully"}), 200
        else:
            return jsonify({"error": "Failed to publish media"}), 500
    else:
        return jsonify({"error": "Failed to upload media"}), 500

if __name__ == "__main__":
    app.run(debug=True)
