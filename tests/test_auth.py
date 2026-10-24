def test_home_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"ResumeIQ" in response.data

def test_registration_and_dashboard(client):
    response = client.post("/register", data={
        "full_name": "Test User",
        "email": "test@example.com",
        "password": "LongEnoughPassword123!"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Your dashboard" in response.data
