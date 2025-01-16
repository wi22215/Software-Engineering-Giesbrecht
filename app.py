from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
import os
from flask_session import Session
from werkzeug.utils import secure_filename
from database.db_manager import ensure_user, get_user_id, save_upload, get_uploads_by_user
from services.scheduler_service import schedule_upload
from services.instagram_service import login_to_instagram, upload_photo_to_instagram, upload_video_to_instagram
from services.instagram_service import cl


# Initialisiere Flask-Anwendung
app = Flask(__name__)

# Konfigurationen
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'supersecretkey'
Session(app)

# Globale Variablen
logged_in_user = None

# Erlaubte Dateiformate
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

        success, error = login_to_instagram(username, password)
        if success:
            logged_in_user = {'username': username}
            ensure_user(username)
            return redirect(url_for('home'))
        else:
            #print(f"Error passed to template: {error}")
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/home', methods=['GET'])
def home():
    global logged_in_user
    if not logged_in_user:
        return redirect(url_for('login'))

    success = request.args.get('success')
    message = request.args.get('message', '')
    return render_template('index.html', success=success, message=message)

@app.route('/upload', methods=['POST'])
def upload():
    global logged_in_user
    if not logged_in_user:
        return redirect(url_for('login'))

    file = request.files.get('file')
    caption = request.form.get('caption')
    upload_time_str = request.form.get('upload_time')
    action = request.form.get('action')

    if not file:
        return redirect(url_for('home', success=False, message="No file provided."))

    # Überprüfen des Dateityps anhand der Listen
    filename = secure_filename(file.filename)
    file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

    if file_extension in ALLOWED_IMAGE_EXTENSIONS:
        file_type = 'image'
    elif file_extension in ALLOWED_VIDEO_EXTENSIONS:
        file_type = 'video'
    else:
        return redirect(url_for('home', success=False, message="Invalid file type."))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    try:
        user_id = get_user_id(logged_in_user['username'])
        if user_id:
            save_upload(user_id, filename, file_path)

        if action == "schedule" and upload_time_str:
            # Wähle die richtige Upload-Funktion basierend auf dem Dateityp
            upload_function = upload_photo_to_instagram if file_type == 'image' else upload_video_to_instagram
            schedule_upload(file_path, caption, upload_time_str, upload_function)
            return redirect(url_for('home', success=True, message="Content scheduled successfully."))
        else:
            # Direkter Upload basierend auf dem Dateityp
            if file_type == 'image':
                upload_photo_to_instagram(file_path, caption)
            else:
                upload_video_to_instagram(file_path, caption)
            return redirect(url_for('home', success=True, message="Upload successful."))
    except Exception as e:
        return redirect(url_for('home', success=False, message=str(e)))


@app.route('/past-uploads', methods=['GET'])
def past_uploads():
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
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "Server is running"}), 200

if __name__ == "__main__":
    app.run(debug=True)
