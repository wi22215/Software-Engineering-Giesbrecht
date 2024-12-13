from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
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

# Initialisiere Instagrapi Client
cl = Client()

# Variable für gespeicherte Login-Daten
logged_in_user = None

# Erlaubte Dateitypen
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4'}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/', methods=['GET', 'POST'])
def login():
    global logged_in_user
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        try:
            # Versuche, den Benutzer mit Instagrapi einzuloggen
            cl.login(username, password)
            logged_in_user = {'username': username, 'password': password}
            return redirect(url_for('home'))  # Weiterleitung zur Upload-Seite
        except Exception as e:
            error_message = str(e)
            if "challenge_required" in error_message:
                error_message = "Login challenge required. Please complete the verification on your Instagram account."
            elif "The password you entered is incorrect" in error_message:
                error_message = "Invalid password. Please try again."
            else:
                error_message = "Invalid username or password."
            return render_template('login.html', error=error_message)
    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    global logged_in_user
    if not logged_in_user:
        return redirect(url_for('login'))  # Weiterleitung zur Login-Seite, falls nicht eingeloggt
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    global logged_in_user
    if not logged_in_user:
        return redirect(url_for('login'))  # Weiterleitung zur Login-Seite, falls nicht eingeloggt

    file = request.files.get('file')
    caption = request.form.get('caption')
    upload_time_str = request.form.get('upload_time')
    action = request.form.get('action')  # Unterscheide zwischen "Upload Now" und "Schedule Upload"

    if not file:
        return jsonify({"error": "No file provided"}), 400

    # Sicherstellen, dass die Datei einen erlaubten Typ hat
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    if allowed_file(filename, ALLOWED_IMAGE_EXTENSIONS):
        # Bild hochladen
        try:
            if action == "schedule" and upload_time_str:
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
            if action == "schedule" and upload_time_str:
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
        # Instagram-Login mit gespeicherten Login-Daten
        cl.photo_upload(file_path, caption)
        print("Photo successfully uploaded to Instagram.")
    except Exception as e:
        raise Exception(f"Instagram API Error: {e}")

# Funktion: Video zu Instagram hochladen
def upload_video_to_instagram(file_path, caption):
    try:
        # Instagram-Login mit gespeicherten Login-Daten
        cl.video_upload(file_path, caption)
        print("Video successfully uploaded to Instagram.")
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

# Route: Vergangene Uploads
@app.route('/past-uploads', methods=['GET'])
def past_uploads():
    try:
        uploads = os.listdir(app.config['UPLOAD_FOLDER'])
        uploads = [f for f in uploads if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
        return render_template('past_uploads.html', uploads=uploads)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Route: Server-Health-Check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "Server is running"}), 200

if __name__ == "__main__":
    app.run(debug=True)
