import unittest
from unittest.mock import MagicMock, patch
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
from flask import json

class TestIntegrationUpload(unittest.TestCase):
    @patch('services.instagram_service.upload_photo_to_instagram')
    def test_upload_with_mocked_instagram(self, mock_instagram_upload):
        """
        Integrationstest für die Upload-Funktion.
        Instagram wird dabei mit MagicMock simuliert.
        """
        # Mock für die Instagram-Antwort
        mock_instagram_upload.return_value = None  # Simuliere erfolgreichen Upload

        # Testclient von Flask erstellen
        with app.test_client() as client:
            # Benutzer als eingeloggt setzen
            with client.session_transaction() as session:
                session['logged_in_user'] = {'username': 'testuser'}

            # Mock-Daten für den Upload
            data = {
                'file': (open('testfile.jpg', 'rb'), 'testfile.jpg'),
                'caption': 'This is an integration test',
                'action': 'upload_now'
            }

            # POST-Anfrage an die /upload-Route
            response = client.post('/upload', data=data, content_type='multipart/form-data')

            # Assertions
            self.assertEqual(response.status_code, 302)  # Überprüfung der Weiterleitung
            self.assertIn('/home', response.location)  # Ziel der Weiterleitung prüfen

            # Sicherstellen, dass der Mock aufgerufen wurde
            mock_instagram_upload.assert_called_once_with(
                'uploads/testfile.jpg', 'This is an integration test'
            )

if __name__ == "__main__":
    unittest.main()
