from app import ensure_user
from database.db_manager import DB_PATH
import sqlite3

def test_ensure_user_in_db():
    """Testet, ob ein Benutzer in der Datenbank eingefügt wird."""
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Benutzer hinzufügen
    ensure_user('testuser')
    
    # Überprüfen, ob der Benutzer existiert
    cursor.execute("SELECT username FROM users WHERE username = ?", ('testuser',))
    user = cursor.fetchone()
    assert user is not None
    assert user[0] == 'testuser'

    # Cleanup
    cursor.execute("DELETE FROM users WHERE username = ?", ('testuser',))
    connection.commit()
    connection.close()
    print("Ein Testuser konnte in der Datenbank angelegt und gelöscht werden.")
