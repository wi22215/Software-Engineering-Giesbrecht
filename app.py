from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime
from threading import Timer
from instagrapi import Client
from werkzeug.utils import secure_filename

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

# Erlaubte Dateitypen
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4'}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/')
def home():
    return render_template('index.html')

# Route: Datei-Upload
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    caption = request.form.get('caption')
    upload_time_str = request.form.get('upload_time')

    if not file:
        return jsonify({"error": "No file provided"}), 400

    # Sicherstellen, dass die Datei einen erlaubten Typ hat
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    if allowed_file(filename, ALLOWED_IMAGE_EXTENSIONS):
        # Bild hochladen
        try:
            if upload_time_str:
                schedule_upload(file_path, caption, upload_time_str, upload_photo_to_instagram)
                return jsonify({"message": "Photo scheduled for upload to Instagram."}), 200
            else:
                upload_photo_to_instagram(file_path, caption)
                return jsonify({"message": "Content successfully uploaded."}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif allowed_file(filename, ALLOWED_VIDEO_EXTENSIONS):
        # Video hochladen
        try:
            if upload_time_str:
                schedule_upload(file_path, caption, upload_time_str, upload_video_to_instagram)
                return jsonify({"message": "Video scheduled for upload to Instagram."}), 200
            else:
                upload_video_to_instagram(file_path, caption)
                return jsonify({"message": "Content successfully uploaded."}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid file format. Only JPG, JPEG, PNG, WEBP, and MP4 are supported."}), 400

# Funktion: Bild zu Instagram hochladen
def upload_photo_to_instagram(file_path, caption):
    try:
        # Instagram-Login
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        print("Successfully logged into Instagram.")

        # Hochladen des Bildes
        media = cl.photo_upload(file_path, caption)
        return {"media_id": media.pk, "caption": caption}
    except Exception as e:
        raise Exception(f"Instagram API Error: {e}")

# Funktion: Video zu Instagram hochladen
def upload_video_to_instagram(file_path, caption):
    try:
        # Instagram-Login
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        print("Successfully logged into Instagram.")

        # Hochladen des Videos
        media = cl.video_upload(file_path, caption)
        return {"media_id": media.pk, "caption": caption}
    except Exception as e:
        raise Exception(f"Instagram API Error: {e}")

# Funktion: Zeitgesteuertes Hochladen planen
def schedule_upload(file_path, caption, upload_time_str, upload_function):
    try:
        upload_time = datetime.strptime(upload_time_str, '%Y-%m-%dT%H:%M')
        delay = (upload_time - datetime.now()).total_seconds()
        if delay > 0:
            Timer(delay, upload_function, [file_path, caption]).start()
            print(f"Upload scheduled for {upload_time_str}")
        else:
            raise Exception("Scheduled time is in the past. Please choose a future time.")
    except ValueError:
        raise Exception("Invalid datetime format. Please use the correct format.")

# Route: Server-Health-Check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "Server is running"}), 200

if __name__ == "__main__":
    app.run(debug=True)