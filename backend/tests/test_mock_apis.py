from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_mock():
    response = client.post("/api/v1/auth/login", json={"username": "test", "password": "pwd"})
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["user"]["id"] == "agent_alpha"

def test_generate_report_mock():
    response = client.post("/api/v1/reports/generate")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment" in response.headers["content-disposition"]
    assert "ignis_report.csv" in response.headers["content-disposition"]
    assert "id,latitude,longitude" in response.text
