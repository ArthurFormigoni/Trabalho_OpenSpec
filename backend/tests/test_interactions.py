import asyncio
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, text
from starlette.websockets import WebSocketDisconnect

from test_api import client, make_png
from app.migrations import migrate
from app.realtime import Realtime


def upload(client):
    return client.post('/images', files={'file': ('image.png', make_png(), 'image/png')}).json()['id']


def test_likes_comments_and_delete(client):
    image_id = upload(client)
    try:
        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(lambda _: client.post(f'/images/{image_id}/likes'), range(10)))
        assert all(result.status_code == 200 for result in results)
        assert sorted(result.json()['likes_count'] for result in results) == list(range(1, 11))
        for value in ('', '   ', 'a' * 1001):
            assert client.post(f'/images/{image_id}/comments', json={'body': value}).status_code == 422
        for i in range(25):
            response = client.post(f'/images/{image_id}/comments', json={'body': f'  Comment {i}  '})
            assert response.status_code == 201
            assert response.json()['comment']['body'] == f'Comment {i}'
            assert response.json()['comment']['created_at'].endswith('Z')
        first = client.get(f'/images/{image_id}/comments').json()
        second = client.get(f'/images/{image_id}/comments?before_id={first["next_cursor"]}').json()
        assert len(first['items']) == 20 and len(second['items']) == 5
        assert not {c['id'] for c in first['items']} & {c['id'] for c in second['items']}
        post = next(row for row in client.get('/images').json() if row['id'] == image_id)
        assert (post['likes_count'], post['comments_count'], post['revision']) == (10, 25, 35)
    finally:
        assert client.delete(f'/images/{image_id}').status_code == 204
    assert client.post(f'/images/{image_id}/likes').status_code == 404
    assert client.post(f'/images/{image_id}/comments', json={'body': 'missing'}).status_code == 404
    assert client.get(f'/images/{image_id}/comments').status_code == 404
    from app.db import engine
    with engine.connect() as connection:
        assert connection.execute(text('SELECT count(*) FROM image_comment WHERE image_id=:id'), {'id': image_id}).scalar() == 0


def test_websocket_origin_and_degraded_state(client):
    with client.websocket_connect('/ws', headers={'origin': 'http://localhost:5173'}) as ws:
        assert ws.receive_json() == {'type': 'status', 'live': False}
    for origin in (None, 'https://untrusted.example'):
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect('/ws', headers={'origin': origin} if origin else {}):
                pass


def test_migration_preserves_legacy_data_and_is_repeatable(tmp_path):
    engine = create_engine(f'sqlite:///{tmp_path / "legacy.db"}')
    with engine.begin() as connection:
        connection.execute(text('CREATE TABLE image (id INTEGER PRIMARY KEY, size_x INTEGER NOT NULL, size_y INTEGER NOT NULL, filesize_bytes BIGINT NOT NULL, image_bytes BLOB NOT NULL)'))
        connection.execute(text("INSERT INTO image VALUES (1, 10, 10, 3, X'010203')"))
    migrate(engine)
    migrate(engine)
    with engine.connect() as connection:
        row = connection.execute(text('SELECT image_bytes, likes_count, comments_count, revision FROM image')).one()
        assert tuple(row) == (b'\x01\x02\x03', 0, 0, 0)
        assert connection.execute(text('SELECT count(*) FROM gallery_migration')).scalar() == 1
    engine.dispose()


def test_publish_failure_and_slow_subscriber():
    class FailingRedis:
        async def publish(self, *args):
            raise OSError('credential must not be logged')
    async def run():
        service = Realtime(SimpleNamespace(redis_url='', redis_channel='test'))
        service.redis = FailingRedis()
        await service.publish('post.updated', 1, {'revision': 1})
        queue, overflow = asyncio.Queue(maxsize=1), asyncio.Event()
        service.clients['slow'] = (queue, overflow)
        service.broadcast({'type': 'status'})
        service.broadcast({'type': 'status'})
        assert overflow.is_set()
    asyncio.run(run())


def test_committed_write_survives_broker_failure(client, monkeypatch):
    from app.main import realtime
    class OfflineRedis:
        async def publish(self, *args):
            raise OSError('offline')
    monkeypatch.setattr(realtime, 'redis', OfflineRedis())
    image_id = upload(client)
    assert client.post(f'/images/{image_id}/likes').json()['likes_count'] == 1
    assert client.post(f'/images/{image_id}/comments', json={'body': 'saved'}).status_code == 201
    assert client.get(f'/images/{image_id}/comments').json()['items'][0]['body'] == 'saved'
    assert client.delete(f'/images/{image_id}').status_code == 204
    monkeypatch.setattr(realtime, 'redis', None)


def test_no_event_on_rollback(client, monkeypatch):
    from app.main import realtime
    from sqlalchemy.orm import Session
    from unittest.mock import AsyncMock
    image_id = upload(client)
    publisher = AsyncMock()
    monkeypatch.setattr(realtime, 'publish', publisher)
    original = Session.commit
    def failure(self):
        raise RuntimeError('simulated commit failure')
    monkeypatch.setattr(Session, 'commit', failure)
    with pytest.raises(RuntimeError):
        client.post(f'/images/{image_id}/likes')
    publisher.assert_not_called()
    monkeypatch.setattr(Session, 'commit', original)
    assert next(row for row in client.get('/images').json() if row['id'] == image_id)['likes_count'] == 0
    client.delete(f'/images/{image_id}')


def test_redis_configuration_requires_verified_tls():
    from app.config import Settings
    from pydantic import ValidationError
    for url in ('https://redis.example', 'rediss://redis.example?ssl_cert_reqs=none'):
        with pytest.raises(ValidationError):
            Settings(redis_url=url)
    async def run():
        service = Realtime(Settings(redis_url='rediss://default:fake@redis.example:6379/0'))
        await service.start()
        options = service.redis.connection_pool.connection_kwargs
        assert options['ssl_cert_reqs'] == 'required'
        assert options['ssl_check_hostname'] is True
        await service.stop()
    asyncio.run(run())
