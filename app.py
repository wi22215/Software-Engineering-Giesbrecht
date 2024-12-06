from flask import Flask, render_template, request, jsonify
import os
from instagrapi import Client

# Initialisiere Flask
app = Flask(__name__)

# Sicherstellen, dass der Upload-Ordner existiert
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Instagram-Konto-Konfiguration
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

# Initialisiere Instagrapi Client
cl = Client()

# Route: Startseite
@app.route('/')
def home():
    return render_template('index.html')

# Route: Datei-Upload
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    caption = request.form.get('caption')

    if not file:
        return jsonify({"error": "No file provided"}), 400

    # Speichere die Datei im Upload-Ordner
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Hochladen zu Instagram
    try:
        response = upload_to_instagram(file_path, caption)
        return jsonify({"message": "File uploaded successfully to Instagram", "response": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Funktion: Bild zu Instagram hochladen
def upload_to_instagram(file_path, caption):
    try:
        # Instagram-Login
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        print("Successfully logged into Instagram.")

        # Hochladen des Bildes
        media = cl.photo_upload(file_path, caption)
        return {"media_id": media.pk, "caption": caption}
    except Exception as e:
        raise Exception(f"Instagram API Error: {e}")

# Route: Server-Health-Check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "Server is running"}), 200

if __name__ == "__main__":
    app.run(debug=True)
