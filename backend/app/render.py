"""Single-service entrypoint serving the API and the built gallery on Render."""

import os

from fastapi.staticfiles import StaticFiles

from .main import app

# Register last so /images, /health and /docs keep their API handlers.
app.mount("/", StaticFiles(directory=os.environ["FRONTEND_DIST"], html=True), name="frontend")
