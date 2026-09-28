## Context

See proposal.md for motivation. The current FastAPI app stores AVIF bytes in PostgreSQL, exposes `/images` and serves the built React frontend on Render through `app.render`. There is no user identity. `create_all` cannot update existing tables, so additive schema migration is required. The final display remains a three-column gallery with a square image region; interaction controls belong below that region.

## Goals / Non-Goals

Goals: durable interactions, atomic concurrent writes, cross-instance distribution, bounded loading, compatibility with the existing image API and same-origin Render deployment.

Non-goals: exactly-once event delivery, durable Redis history, unique-human likes, authentication, comment moderation tools or a general social network.

## Decisions

### PostgreSQL owns post state

Add `likes_count BIGINT NOT NULL DEFAULT 0`, `comments_count BIGINT NOT NULL DEFAULT 0` and `revision BIGINT NOT NULL DEFAULT 0` to `image`, all nonnegative. Add `image_comment(id, image_id, body, created_at)` with FK `ON DELETE CASCADE`, UTC timestamp, text length constraint and composite index `(image_id, id)`.

Use atomic `UPDATE ... SET likes_count = likes_count + 1, revision = revision + 1 RETURNING ...`. For comments, lock/update the parent and insert the comment in one transaction, incrementing comment count and revision. Use the same parent-row serialization for deletion; check missing images and map concurrent deletion to 404. This avoids lost updates, orphaned records and counting by browser. Redis counters were rejected because database and broker restarts must not erase interactions.

### HTTP writes and paginated reads

`POST /images/{id}/likes` returns 200 with `{image_id, likes_count, comments_count, revision}`. Each request counts once; separate repeated requests intentionally add likes. No automatic retry of mutations: a network interruption after commit can leave the client unsure; refresh HTTP state and let the visitor choose another action.

`POST /images/{id}/comments` accepts `{body}` and returns 201 with `{comment, likes_count, comments_count, revision}`. The comment includes `id`, `image_id`, `body`, `created_at`. Trim and validate 1–1000 characters before persistence; render React text only. `GET /images/{id}/comments?before_id=...&limit=20` returns `{items, next_cursor}`, IDs descending, max 100. The UI displays newest comments first and loads older pages explicitly.

`GET /images` adds the three state fields without removing prior fields. Upload responses use the same extended image representation. Existing data starts at zero. Single-comment deletion/editing is excluded because there is no author identity or moderation role.

### Redis Pub/Sub and receive-only browser WebSocket

Use the async Redis client, one subscription per API process, and a local connection manager attached in the FastAPI lifespan shared by local and Render entrypoints. Move blocking database work off the event loop; publish only after commit. Publish failures are logged without URLs or credentials and do not replace successful HTTP responses.

Expose `/ws` before the root static mount. Events use `{event_id, type, image_id, revision?, data}` with types `image.created`, `image.deleted`, `post.updated`. Creation includes image metadata, deletion the image ID, and post updates authoritative counters plus optional created comment. Use one Redis delivery path rather than local broadcast plus broker echo. Bound each client's send queue; disconnect slow consumers so one browser cannot block others. Cancel subscription/reconnect tasks and close clients on shutdown.

WebSocket carries events and heartbeat/status messages, not commands. Origin validation is independent of HTTP CORS: reject missing or unlisted origins. Broker connects with timeout and exponential reconnect backoff capped at 30 seconds. A periodic server heartbeat allows stale sockets to close and reconnect.

### Event loss and ordering

Pub/Sub is transient. Avoid an outbox in this first version because bounded eventual consistency is sufficient. Clients apply counts by revision, deduplicate comment IDs/events and never blindly increment on a notification. Older HTTP responses must also be gated by revision. Serialize full-gallery refreshes, queue events arriving during a refresh and reconcile after the response so stale requests cannot resurrect deleted posts. Deletion notifications remove the card; reconnect/foreground and periodic synchronization settle missed events.

Connect first and synchronize after subscription readiness; re-fetch after broker recovery, WebSocket reconnect and foreground return. While the page is active, refresh gallery metadata and the newest page of open comment sections every 30 seconds, including when live mode is unavailable. On comment events invalidate/refetch the newest page and merge by ID with loaded older pages. Use capped exponential browser reconnect backoff with jitter; show a subtle disconnected indicator, not repeated error toasts.

### Environment and deployment

- `DATABASE_URL`: existing PostgreSQL connection, unchanged.
- `REDIS_URL`: server-only connection such as `rediss://default:REPLACE_ME@redis.example.com:6379/0`; absent means degraded HTTP-only operation. Require a standard Redis protocol endpoint, not an HTTP REST endpoint.
- `REDIS_CHANNEL`: default `photo-gallery:events`; assign different names for separate environments.
- `WS_ALLOWED_ORIGINS`: comma-separated list, locally `http://localhost:5173,http://127.0.0.1:5173`; on Render supply the exact HTTPS service/custom-domain origins. No wildcard fallback. Derive browser `ws://` or `wss://` from the existing API URL, or `window.location` when same-origin.

Keep TLS certificate verification enabled for `rediss://`; never ship Redis credentials in a VITE variable, source file or build argument. Add placeholders to both env examples and inputs to `render.yaml`; document health behavior. `/health` remains liveness and does not fail solely because Redis is unavailable.

## Risks / Trade-offs

- Anonymous repeated likes and comments can be abused → clearly present likes as interactions, not unique people; validate comment lengths and bound requests/connections. Strong identity and moderation remain future scope.
- Commit succeeds and event publication fails → retain success, reconcile with authoritative HTTP state within the active refresh interval.
- Concurrent deploys may race migrations → versioned migration in a transaction with a PostgreSQL advisory lock; repeated execution must be safe.
- Migration takes locks on the live Aiven database → test with existing data locally, back up before applying remotely, preserve image bytes and avoid destructive reset.
- Public image deletion already exists without login → retain the existing behavior; comments follow their parent deletion.
- Provider connection limits → one subscription per API process, bounded connection pool and documented Redis monitoring.

## Migration Plan

1. Implement a versioned migration runner and an additive migration for existing installations; fresh databases must reach the same schema. Existing `create_all` alone is insufficient.
2. Verify migration and rerun safety against a disposable PostgreSQL containing images; test constraints and cascade behavior in PostgreSQL, not SQLite alone.
3. During implementation, run local application with test services, then configure actual cloud Redis credentials through env when available. Never include them in artifacts or commits.
4. Before deploying to Aiven, create a recoverable backup and run the reviewed migration. The user authorized database changes if needed; do not clear existing images or interactions.
5. Integrate the migration runner before Uvicorn starts in deployment so Render does not serve code against an old schema; make concurrent starts safe. Configure Redis and allowed origins, then verify two clients and two API instances.
6. Roll back the application if required while retaining additive columns and tables. Do not drop persisted likes/comments during rollback; old API versions can ignore the new fields.

## Open Questions

The cloud Redis endpoint, credentials and optional provider CA are supplied during implementation through environment variables. They do not change the API or data model; without them, cloud connectivity remains unverified while local integration tests can proceed.
