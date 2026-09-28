## Purpose

Permitir interação pública com imagens tratadas como posts, por meio de likes globais e comentários anônimos persistentes, sem exigir autenticação.

## ADDED Requirements

### Requirement: Persistent global likes
The system SHALL accept `POST /images/{id}/likes` without login and atomically increment a nonnegative global `likes_count` by one per successful request. The response SHALL include the authoritative count and post revision. No browser identity, unique-person limit, or unlike operation SHALL be required.

#### Scenario: Repeated and concurrent likes
- **WHEN** two visitors send a total of ten successful like requests to the same post, including repeated clicks
- **THEN** the stored count increases by exactly ten and survives API and Redis restarts

#### Scenario: Missing post
- **WHEN** a visitor likes an image that no longer exists
- **THEN** the API returns 404 and creates no interaction

### Requirement: Anonymous comments
The system SHALL accept `POST /images/{id}/comments` with a `body` of 1 to 1000 characters after trimming, persist it with an ID and server-generated UTC timestamp, and return 201 with the created comment and current post counters and revision. Comments SHALL be presented as anonymous plain text. Invalid content SHALL return 422 without persistence; missing images SHALL return 404.

#### Scenario: Persist and display comment
- **WHEN** a visitor submits a valid comment and another visitor reloads the post
- **THEN** both can read the same comment and timestamp without signing in

#### Scenario: Invalid or executable text
- **WHEN** a visitor submits only whitespace or more than 1000 characters
- **THEN** the request is rejected with 422
- **AND** valid-length text containing HTML is displayed as text and never executed

### Requirement: Bounded comment listing
The system SHALL expose `GET /images/{id}/comments` with `limit` default 20, allowed range 1 to 100, and an optional positive `before_id` cursor. Results SHALL be ordered by descending ID and include `next_cursor`, allowing older comments to be loaded without duplicates in stable data. Missing images SHALL return 404.

#### Scenario: Read older comments
- **WHEN** a post has 25 comments and a visitor loads the default page then uses its next cursor
- **THEN** the visitor receives the newest 20 and then the remaining 5 without overlap

### Requirement: Post interface and compatibility
The gallery SHALL retain current upload, deletion, AVIF processing and maximum three-column behavior. Each post SHALL show the square image area, accessible like control, counters, and expandable comments with input, submission and loading/error states. `GET /images` SHALL retain existing fields and add `likes_count`, `comments_count` and `revision`. Pending controls SHALL prevent accidental double submission, and failed requests SHALL not be automatically replayed.

#### Scenario: Existing image
- **WHEN** the migration runs on a gallery containing images
- **THEN** every image remains available with zero initial interaction counts and its original image bytes

#### Scenario: Submit failure
- **WHEN** a comment request fails
- **THEN** the UI preserves the draft and shows an error without reporting success or incrementing the count

### Requirement: Delete related interactions
The system SHALL delete all comments belonging to an image when that image is deleted, with no orphaned interactions even during concurrent requests.

#### Scenario: Delete a commented post
- **WHEN** a visitor deletes an image containing likes and comments
- **THEN** its image record and comments are removed and subsequent interaction requests return 404
