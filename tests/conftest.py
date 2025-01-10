import sys
import os
from pathlib import Path
import pytest

# Hauptverzeichnis zum Python-Pfad hinzufügen
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app import app  # Importiere die Flask-App


@pytest.fixture
def client():
    """Test-Client für Flask."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
