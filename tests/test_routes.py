def test_login_page(client):
    """Testet, ob die Login-Seite erreichbar ist."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Login" in response.data  # Überprüft, ob "Login" im HTML enthalten ist

def test_login_success(client, mocker):
    """Testet erfolgreiches Login."""
    # Mock für `cl.login` (erfolgreicher Login)
    def mock_login(username, password):
        if username == "testuser" and password == "correctpassword":
            return True
        raise Exception("Invalid username or password")

    # Mock die `login_to_instagram`-Funktion statt `cl.login`
    mocker.patch('app.cl.login', side_effect=mock_login)

    # Anfrage mit korrekten Daten
    response = client.post('/', data={
        'username': 'testuser',
        'password': 'correctpassword'
    })

    # Erwartungen:
    assert response.status_code == 302  # Weiterleitung
    assert '/home' in response.headers['Location']  # Ziel der Weiterleitung
    print("Ein erfolgreicher Login hat geklappt.")

def test_login_failure(client, mocker):
    """Testet Login mit falschen Daten."""
    # Mock die `login_to_instagram`-Funktion für einen fehlgeschlagenen Login
    def mock_login(username, password):
        if username == "testuser" and password == "correctpassword":
            return True  # Login erfolgreich
        raise Exception("Invalid username or password")  # Login fehlschlagen

    mocker.patch('app.cl.login', side_effect=mock_login)

    # Falsche Login-Daten
    response = client.post('/', data={
        'username': 'testuser',
        'password': 'wrongpassword'
    })

    assert response.status_code == 200  # Kein Redirect, bleibt auf der Login-Seite
    assert b"Invalid username or password" in response.data  # Fehlernachricht angezeigt
    print("Ein falscher Login ist korrekterweise fehlgeschlagen.")

