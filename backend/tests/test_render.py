from fastapi.testclient import TestClient


def test_render_serves_frontend_and_preserves_api(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'render.sqlite3'}")
    from app.config import get_settings
    get_settings.cache_clear()
    static = tmp_path / "static"
    static.mkdir()
    (static / "index.html").write_text("<html>Photo Gallery</html>", encoding="utf-8")
    (static / "assets").mkdir()
    (static / "assets" / "app.js").write_text("console.log('gallery');", encoding="utf-8")
    monkeypatch.setenv("FRONTEND_DIST", str(static))

    from app.render import app

    try:
        with TestClient(app) as client:
            assert client.get("/").text == "<html>Photo Gallery</html>"
            assert client.get("/assets/app.js").status_code == 200
            assert client.get("/health").json() == {"status": "ok"}
            assert client.get("/images").json() == []
            assert client.get("/images/999/content").status_code == 404
            assert client.get("/.env").status_code == 404
    finally:
        app.router.routes[:] = [route for route in app.router.routes if route.name != "frontend"]
