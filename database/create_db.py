import sqlite3

def create_database():
    # Verbindung zur SQLite-Datenbank herstellen (erstellt die Datei, falls sie nicht existiert)
    connection = sqlite3.connect("file_management.db")
    cursor = connection.cursor()

    # Tabelle für Nutzer erstellen
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Tabelle für Uploads erstellen
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

    # Änderungen speichern und Verbindung schließen
    connection.commit()
    connection.close()
    print("Datenbank und Tabellen wurden erfolgreich erstellt.")

if __name__ == "__main__":
    create_database()
