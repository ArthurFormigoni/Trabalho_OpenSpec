import asyncio
import json
import logging
from contextlib import suppress
from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class Realtime:
    def __init__(self, settings):
        self.settings = settings
        self.redis = None
        self.task = None
        self.connected = False
        self.clients = {}

    async def start(self):
        if self.settings.redis_url:
            from redis.asyncio import Redis
            options = {"ssl_cert_reqs": "required", "ssl_check_hostname": True} if self.settings.redis_url.startswith("rediss:") else {}
            self.redis = Redis.from_url(self.settings.redis_url, decode_responses=True,
                                        socket_connect_timeout=3, socket_timeout=3,
                                        max_connections=20, **options)
            self.task = asyncio.create_task(self.listen())

    def broadcast(self, payload):
        for queue, overflow in list(self.clients.values()):
            try:
                queue.put_nowait(payload)
            except asyncio.QueueFull:
                overflow.set()

    async def listen(self):
        delay = 1
        while True:
            try:
                async with self.redis.pubsub() as subscription:
                    await subscription.subscribe(self.settings.redis_channel)
                    self.connected = True
                    self.broadcast({"type": "status", "live": True})
                    delay = 1
                    while True:
                        message = await subscription.get_message(ignore_subscribe_messages=True, timeout=1)
                        if message and message["type"] == "message":
                            try:
                                payload = json.loads(message["data"])
                                if isinstance(payload, dict) and payload.get("type") in {"image.created", "image.deleted", "post.updated"}:
                                    self.broadcast(payload)
                            except (ValueError, TypeError):
                                logger.warning("Ignored invalid Redis event")
            except asyncio.CancelledError:
                raise
            except Exception:
                self.connected = False
                self.broadcast({"type": "status", "live": False})
                logger.warning("Redis unavailable; HTTP synchronization remains available")
                await asyncio.sleep(delay)
                delay = min(delay * 2, 30)

    async def publish(self, event_type, image_id, data=None):
        if not self.redis:
            return
        payload = {"event_id": str(uuid4()), "type": event_type, "image_id": image_id, "data": data or {}}
        if data and "revision" in data:
            payload["revision"] = data["revision"]
        try:
            await asyncio.wait_for(self.redis.publish(self.settings.redis_channel, json.dumps(payload)), timeout=3)
        except Exception:
            logger.warning("Event publication failed after commit; clients will resynchronize")

    async def stop(self):
        if self.task:
            self.task.cancel()
            with suppress(asyncio.CancelledError):
                await self.task
        for _, overflow in list(self.clients.values()):
            overflow.set()
        if self.redis:
            await self.redis.aclose()
        self.connected = False

    async def serve(self, socket: WebSocket):
        if socket.headers.get("origin") not in self.settings.ws_origin_list:
            await socket.close(code=1008)
            return
        if len(self.clients) >= 500:
            await socket.close(code=1013)
            return
        await socket.accept()
        queue, overflow = asyncio.Queue(maxsize=64), asyncio.Event()
        self.clients[socket] = (queue, overflow)
        queue.put_nowait({"type": "status", "live": self.connected})

        async def send():
            while True:
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=15)
                except asyncio.TimeoutError:
                    payload = {"type": "heartbeat", "live": self.connected}
                await asyncio.wait_for(socket.send_json(payload), timeout=5)

        async def receive():
            while True:
                message = await socket.receive()
                if message["type"] == "websocket.disconnect":
                    return
                # Browser connections receive events; no mutation commands accepted.
                await socket.close(code=1008)
                return

        tasks = [asyncio.create_task(send()), asyncio.create_task(receive()), asyncio.create_task(overflow.wait())]
        try:
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        finally:
            self.clients.pop(socket, None)
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            with suppress(RuntimeError, WebSocketDisconnect):
                await socket.close(code=1013 if overflow.is_set() else 1000)
