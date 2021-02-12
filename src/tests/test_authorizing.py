from flask_dance.consumer.storage import MemoryStorage
from app import app, github_bp
import json, os


def test_index_unauthorized(monkeypatch):
    storage = MemoryStorage()
    monkeypatch.setattr(github_bp, "storage", storage)
    with app.test_client() as client:
        response = client.get("/", base_url="https://localhost:5000")

    assert response.status_code == 302
    assert response.headers[
        "Location"] == "https://localhost:5000/login/github"


def test_index_authorized(monkeypatch):
    # get the access token from runnin the applicatin to access GITHUB_OAUTH_CLIENT_ID
    # it will be written on stdout
    # ex: 2079edddcd69a3173322ff1963755a3f3d58cd3e"
    FAKE_TOKEN = os.environ.get("FAKE_TOKEN", "supersekrit")
    storage = MemoryStorage({"access_token": f"{FAKE_TOKEN}"})
    monkeypatch.setattr(github_bp, "storage", storage)

    with app.test_client() as client:
        response = client.get("https://localhost:5000/contributors")
    success = json.loads(response.get_data())["success"]
    assert response.status_code == 200
    assert success == True