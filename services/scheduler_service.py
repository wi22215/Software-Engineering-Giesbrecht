from datetime import datetime
from threading import Timer

def schedule_upload(file_path, caption, upload_time_str, upload_function):
    """
    Plant einen zeitgesteuerten Upload.
    :param file_path: Pfad zur Datei
    :param caption: Beschreibung der Datei
    :param upload_time_str: Geplanter Upload-Zeitpunkt (Format: YYYY-MM-DDTHH:MM)
    :param upload_function: Upload-Funktion (z. B. upload_photo_to_instagram)
    """
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
