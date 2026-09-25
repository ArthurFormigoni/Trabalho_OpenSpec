import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image


@pytest.fixture()
def client(tmp_path, monkeypatch):
    database = tmp_path / "test.sqlite3"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database}")
    from app import config
    config.get_settings.cache_clear()
    from app.main import app
    with TestClient(app) as test_client:
        yield test_client


def make_png(size=(200, 200)):
    image = Image.new("RGB", size, (65, 105, 225))
    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def test_empty_list(client):
    response = client.get("/images")
    assert response.status_code == 200
    assert response.json() == []


def test_invalid_aspect_ratio(client):
    response = client.post("/images", files={"file": ("tall.png", make_png((100, 300)), "image/png")})
    assert response.status_code == 400
    assert "proporção" in response.json()["detail"]


def test_invalid_file(client):
    response = client.post("/images", files={"file": ("bad.bin", b"not an image", "application/octet-stream")})
    assert response.status_code == 400


def test_upload_content_and_delete(client):
    response = client.post("/images", files={"file": ("square.png", make_png(), "image/png")})
    assert response.status_code == 201
    payload = response.json()
    assert payload["filesize_bytes"] <= 1_048_576
    assert payload["content_type"] == "image/avif"

    content = client.get(payload["image_url"])
    assert content.status_code == 200
    assert content.headers["content-type"] == "image/avif"
    assert "no-store" in content.headers["cache-control"]

    deleted = client.delete(f"/images/{payload['id']}")
    assert deleted.status_code == 204
    assert client.get("/images").json() == []


def test_delete_missing_image(client):
    assert client.delete("/images/999").status_code == 404
