from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from models import db  # Importiere die `db`-Instanz aus models.py

# Lade Umgebungsvariablen
load_dotenv()

# Flask-Konfiguration
app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "instance", "uploads.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisiere die Datenbank
db.init_app(app)

# Sicherstellen, dass der Upload-Ordner existiert
UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Importiere Modelle (auslagern in models.py)
from models import Media

# Routen
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    caption = request.form.get('caption', '')

    if not file:
        return jsonify({"error": "No file provided"}), 400

    # Speichere Datei
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # In der Datenbank speichern
    media = Media(filename=file.filename, filepath=file_path, caption=caption)
    db.session.add(media)
    db.session.commit()

    return jsonify({"message": "File uploaded successfully", "media_id": media.id}), 201

@app.route('/media', methods=['GET'])
def get_media():
    media_list = Media.query.all()
    response = [
        {
            "id": media.id,
            "filename": media.filename,
            "filepath": media.filepath,
            "caption": media.caption,
            "uploaded_at": media.uploaded_at
        }
        for media in media_list
    ]
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(debug=True)
