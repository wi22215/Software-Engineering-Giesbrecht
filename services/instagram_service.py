from instagrapi import Client

# Initialisiere Instagrapi Client
cl = Client()

def login_to_instagram(username, password):
    """Loggt den Benutzer in Instagram ein."""
    try:
        cl.login(username, password)
        return True, None
    except Exception as e:
        return False, str(e)

def upload_photo_to_instagram(file_path, caption):
    """Lädt ein Foto zu Instagram hoch."""
    try:
        cl.photo_upload(file_path, caption)
        print("Photo successfully uploaded to Instagram.")
    except Exception as e:
        raise Exception(f"Instagram API Error: {e}")

def upload_video_to_instagram(file_path, caption):
    """Lädt ein Video zu Instagram hoch."""
    try:
        cl.video_upload(file_path, caption)
        print("Video successfully uploaded to Instagram.")
    except Exception as e:
        raise Exception(f"Instagram API Error: {e}")
