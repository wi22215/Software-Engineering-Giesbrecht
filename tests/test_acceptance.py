import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Konfiguration für Selenium
BASE_URL = "http://localhost:5000"  # URL der laufenden Flask-App
UPLOAD_FILE_PATH = os.path.abspath("testfile.jpg")  # Absoluter Pfad zur Datei für den Upload

# Dynamische Ermittlung des Browsers
def get_browser_driver():
    try:
        driver = webdriver.Chrome()
        driver.set_window_size(1920, 1080)
        return driver
    except Exception:
        try:
            driver = webdriver.Firefox()
            driver.set_window_size(1920, 1080)
            return driver
        except Exception:
            raise RuntimeError("Kein unterstützter Browser-Treiber verfügbar. Stellen Sie sicher, dass entweder ChromeDriver oder GeckoDriver installiert ist.")

def test_positive_flow():
    """Testet Login, Datei-Upload und Beschreibungseingabe."""
    driver = get_browser_driver()
    driver.get(f"{BASE_URL}/")

    try:
        # Login testen
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )

        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.TAG_NAME, "button")

        username_input.send_keys("clejaslau")
        password_input.send_keys("SWEProjekt")
        login_button.click()

        # Überprüfen, ob die Weiterleitung erfolgreich war
        WebDriverWait(driver, 10).until(
            EC.url_contains("/home")
        )
        print("Login erfolgreich.")

        # Datei auswählen und Beschreibung eingeben
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "file"))
        )
        file_input = driver.find_element(By.ID, "file")
        file_input.send_keys(UPLOAD_FILE_PATH)

        caption_input = driver.find_element(By.ID, "caption")
        caption_input.send_keys("This is an automated acceptance test")

        # Datei hochladen
        upload_button = driver.find_element(By.ID, "uploadNowButton")
        upload_button.click()

        # Überprüfen, ob der Upload erfolgreich war
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        print("Upload erfolgreich.")

    except Exception as e:
        print(f"Test fehlgeschlagen: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Starte positiven Flow-Test...")
    test_positive_flow()
