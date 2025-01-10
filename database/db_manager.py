import sqlite3

# Pfad zur SQLite-Datenbank
DB_PATH = "database/file_management.db"

def create_tables():
    """
    Erstellt die notwendigen Tabellen in der Datenbank, falls sie nicht existieren.
    - Tabelle 'users': Speichert Benutzerinformationen.
    - Tabelle 'uploads': Speichert Upload-Informationen und referenziert 'users'.
    """
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()

        # Benutzer-Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Uploads-Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploads (
            upload_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        )
        ''')

        connection.commit()

def ensure_user(username):
    """
    Fügt einen Benutzer zur Datenbank hinzu, falls er nicht existiert.
    :param username: Name des Benutzers
    """
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if not user:
            cursor.execute(
                "INSERT INTO users (username, created_at) VALUES (?, CURRENT_TIMESTAMP)", (username,)
            )
            connection.commit()

def get_user_id(username):
    """
    Holt die Benutzer-ID eines gegebenen Benutzernamens.
    :param username: Name des Benutzers
    :return: Benutzer-ID oder None
    """
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        return user[0] if user else None

def save_upload(user_id, file_name, file_path):
    """
    Speichert einen Upload in der Datenbank.
    :param user_id: ID des Benutzers
    :param file_name: Name der hochgeladenen Datei
    :param file_path: Pfad zur Datei
    """
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO uploads (user_id, file_name, file_path, upload_date) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
            (user_id, file_name, file_path),
        )
        connection.commit()

def get_uploads_by_user(username):
    """
    Holt alle Uploads eines Benutzers.
    :param username: Name des Benutzers
    :return: Liste der Uploads
    """
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT file_name, file_path, upload_date
            FROM uploads
            JOIN users ON uploads.user_id = users.user_id
            WHERE users.username = ?
            """,
            (username,)
        )
        return cursor.fetchall()
