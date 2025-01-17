from instagrapi import Client

# Instagrapi Client
cl = Client()

def login_to_instagram(username, password):
    """
    Loggt einen Benutzer in Instagram ein.
    :param username: Instagram-Benutzername
    :param password: Passwort
    :return: Tuple (bool, str) - Erfolg und Fehlermeldung (falls vorhanden)
    """
    try:
        cl.login(username, password)
        return True, None
    except Exception as e:
        return False, str(e)

def upload_photo_to_instagram(file_path, caption):
    """
    Lädt ein Foto zu Instagram hoch.
    :param file_path: Pfad zur Bilddatei
    :param caption: Bildbeschreibung
    """
    try:
        cl.photo_upload(file_path, caption)
        print("Photo successfully uploaded to Instagram.")
    except Exception as e:
        raise Exception(f"Instagram API Error: {e}")

def upload_video_to_instagram(file_path, caption):
    """
    Lädt ein Video zu Instagram hoch.
    :param file_path: Pfad zur Videodatei
    :param caption: Videobeschreibung
    """
    try:
        cl.video_upload(file_path, caption)
        print("Video successfully uploaded to Instagram.")
    except Exception as e:
        raise Exception(f"Instagram API Error: {e}")

def upload_reel_to_instagram(file_path, caption):
    """
    Lädt ein Reel zu Instagram hoch.
    :param file_path: Pfad zur Videodatei
    :param caption: Beschreibung des Reels
    """
    try:
        cl.clip_upload(file_path, caption)
        print("Reel successfully uploaded to Instagram.")
    except Exception as e:
        raise Exception(f"Instagram API Error: {e}")

