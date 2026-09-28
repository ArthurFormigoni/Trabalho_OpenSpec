"""Force database isolation before application modules are imported by pytest."""
import os
import tempfile
from pathlib import Path

_test_directory = tempfile.TemporaryDirectory(prefix="gallery-tests-")
os.environ["DATABASE_URL"] = "sqlite:///" + (Path(_test_directory.name) / "suite.sqlite3").as_posix()
os.environ["REDIS_URL"] = ""


def pytest_sessionfinish(session, exitstatus):
    from app.db import engine
    engine.dispose()
    _test_directory.cleanup()
