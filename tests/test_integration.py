import sys, os
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.instagram_service import upload_photo_to_instagram
from app import app

class TestLoginIntegration(unittest.TestCase):
    @patch('services.instagram_service.login_to_instagram')
    def test_login_success(self, mock_login):
        """
        Teste erfolgreichen Login.
        """
        mock_login.return_value = (True, None)  # Simuliere erfolgreichen Login

        with app.test_client() as client:
            response = client.post('/', data={
                'username': 'clejaslau',
                'password': 'SWEProjekt'
            })

            self.assertEqual(response.status_code, 302)  # Redirect erwartet
            self.assertIn('/home', response.location)  # Ziel der Weiterleitung

    @patch('services.instagram_service.login_to_instagram')
    def test_login_failure(self, mock_login):
        """
        Teste fehlgeschlagenen Login.
        """
        mock_login.return_value = (False, "Invalid credentials")  # Simuliere fehlgeschlagenen Login

        with app.test_client() as client:
            response = client.post('/', data={
                'username': 'testuser',
                'password': 'wrongpassword'
            })

            self.assertEqual(response.status_code, 200)  # Keine Weiterleitung
            self.assertIn(b"Invalid username or password", response.data)  # Fehlermeldung prüfen


    @patch('database.db_manager.get_uploads_by_user')
    def test_past_uploads(self, mock_get_uploads_by_user):
        """
        Integrationstest für die Anzeige der hochgeladenen Inhalte.
        """
        # Simuliere Rückgabe von Upload-Daten
        mock_get_uploads_by_user.return_value = [
            ('testfile.jpg', '/uploads/testfile.jpg', '2025-01-14 10:00:00'),
            ('testfile.jpg', '/uploads/testfile.png', '2025-01-14 12:00:00')
        ]

        with app.test_client() as client:
            # Benutzer als eingeloggt setzen
            with client.session_transaction() as session:
                session['logged_in_user'] = {'username': 'testuser'}

            # GET-Anfrage an die /past-uploads-Route
            response = client.get('/past-uploads')

            # Assertions
            self.assertEqual(response.status_code, 200)  # Erfolgreiche Antwort
            self.assertIn(b'testfile.jpg', response.data)  # Erster Upload vorhanden
            self.assertIn(b'testfile.jpg', response.data)  # Zweiter Upload vorhanden

if __name__ == "__main__":
    unittest.main()


if __name__ == "__main__":
    unittest.main()
