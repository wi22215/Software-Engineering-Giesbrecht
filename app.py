from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
from database.db_manager import ensure_user, get_user_id, save_upload, get_uploads_by_user
from services.scheduler_service import schedule_upload
from services.instagram_service import login_to_instagram, upload_photo_to_instagram

# Initialisiere Flask-Anwendung
app = Flask(__name__)

# Konfigurationen
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Globale Variablen
logged_in_user = None

# Erlaubte Dateiformate
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4'}

def allowed_file(filename, allowed_extensions):
    """
    Überprüft, ob die Datei einen erlaubten Typ hat.
    :param filename: Dateiname
    :param allowed_extensions: Set erlaubter Dateiendungen
    :return: True, wenn der Typ erlaubt ist, sonst False
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/', methods=['GET', 'POST'])
def login():
    """
    Login-Seite für die Benutzeranmeldung.
    - POST: Überprüft Login-Daten und leitet zum Home weiter.
    - GET: Zeigt Login-Formular.
    """
    global logged_in_user
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        success, error = login_to_instagram(username, password)
        if success:
            logged_in_user = {'username': username}
            ensure_user(username)
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/home', methods=['GET'])
def home():
    """
    Home-Seite nach dem Login.
    """
    global logged_in_user
    if not logged_in_user:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """
    Upload-Route:
    - Akzeptiert eine Datei, eine Beschreibung und eine optionale Upload-Zeit.
    - Unterstützt sofortige und geplante Uploads.
    """
    global logged_in_user
    if not logged_in_user:
        return redirect(url_for('login'))

    file = request.files.get('file')
    caption = request.form.get('caption')
    upload_time_str = request.form.get('upload_time')
    action = request.form.get('action')

    if not file:
        return jsonify({"error": "No file provided"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    if allowed_file(filename, ALLOWED_IMAGE_EXTENSIONS) or allowed_file(filename, ALLOWED_VIDEO_EXTENSIONS):
        try:
            user_id = get_user_id(logged_in_user['username'])
            if user_id:
                save_upload(user_id, filename, file_path)

            if action == "schedule" and upload_time_str:
                schedule_upload(file_path, caption, upload_time_str, upload_photo_to_instagram)
                return jsonify({"message": "Content scheduled for upload to Instagram."}), 200
            else:
                upload_photo_to_instagram(file_path, caption)
                return jsonify({"message": "Content successfully uploaded."}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Invalid file format. Only JPG, JPEG, PNG, WEBP, and MP4 are supported."}), 400

@app.route('/past-uploads', methods=['GET'])
def past_uploads():
    """
    Route für vergangene Uploads:
    - Holt und zeigt alle Uploads des aktuell eingeloggten Benutzers.
    """
    global logged_in_user
    if not logged_in_user:
        return redirect(url_for('login'))

    try:
        uploads = get_uploads_by_user(logged_in_user['username'])
        upload_list = [{"file_name": row[0], "file_path": row[1], "upload_date": row[2]} for row in uploads]
        return render_template('past_uploads.html', uploads=upload_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """
    Liefert eine hochgeladene Datei zurück.
    :param filename: Name der Datei
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health-Check-Route, um sicherzustellen, dass der Server läuft.
    """
    return jsonify({"status": "OK", "message": "Server is running"}), 200

if __name__ == "__main__":
    app.run(debug=True)
