## Purpose

Sincronizar posts e interações entre visitantes e instâncias da API por WebSocket e Redis remoto, com configuração por ambiente e recuperação após interrupções.

## ADDED Requirements

### Requirement: Cross-instance real-time events
The system SHALL expose `/ws` and use cloud Redis to distribute committed image creation, deletion, likes and comments to connected clients across API instances. Messages SHALL include a unique event ID, event type, image ID and, for interaction updates, the authoritative counters and revision. Events SHALL contain neither image binary content nor connection credentials.

#### Scenario: Two API instances
- **WHEN** an interaction commits on instance A while a visitor is connected to instance B
- **THEN** that visitor receives an event and sees the current interaction state without reloading the page

#### Scenario: Failed transaction
- **WHEN** a database transaction fails
- **THEN** no successful interaction event is published

### Requirement: Ordering and recovery
Clients SHALL apply authoritative counts rather than incrementing on events and SHALL ignore duplicate or older revisions. Clients SHALL refresh HTTP state after WebSocket connection/reconnection, on foreground return, and at a bounded periodic interval of at most 30 seconds while active. Comment lists that are open SHALL be refreshed when relevant events arrive. Clients SHALL reconnect with bounded backoff and show when live updates are unavailable.

#### Scenario: Duplicate event
- **WHEN** a like response and duplicated or delayed events describe the same or an older revision
- **THEN** the displayed count neither increases twice nor moves backwards

#### Scenario: Missed deletion
- **WHEN** a client misses a deletion while disconnected and reconnects
- **THEN** HTTP synchronization removes the deleted post and its visible comments

### Requirement: Remote Redis environment configuration
The system SHALL support `REDIS_URL` with `redis://` and `rediss://`, `REDIS_CHANNEL` for isolation and `WS_ALLOWED_ORIGINS` for browser WebSocket origin validation. TLS certificate verification SHALL remain enabled for `rediss://`. Examples and Render settings SHALL use placeholders or secret inputs, and credentials SHALL remain server-side and absent from logs.

#### Scenario: Cloud configuration
- **WHEN** a valid TLS Redis URL, channel and deployed frontend origin are supplied through environment variables
- **THEN** real-time distribution connects securely without source code changes

#### Scenario: Disallowed origin
- **WHEN** a WebSocket handshake supplies an unlisted Origin or no Origin
- **THEN** the server rejects the connection

### Requirement: Redis outage does not lose persistent writes
The system SHALL keep HTTP gallery and interaction operations available when Redis is missing or unavailable, subject to PostgreSQL availability. Successfully committed requests SHALL remain successful if event publication fails. Live distribution SHALL recover automatically after Redis returns; connected clients SHALL resynchronize without replaying mutations.

#### Scenario: Broker failure after commit
- **WHEN** a comment commits but Redis publication fails
- **THEN** the API returns the persisted result, subsequent HTTP reads include it, and clients converge through HTTP synchronization
