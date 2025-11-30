# API Contract — Singularity

**OpenAPI spec:** `apps/api/openapi.yaml` (OpenAPI 3.0.3)

---

## Authentication

### Mechanism
- **JWT Bearer tokens** via `Authorization: Bearer <token>` header.
- Tokens issued by the API on successful login or registration (expires in 7 days by default).

### Flow
1. `POST /users/register` → creates user, returns `{ token, user, expiresIn }`.
2. `POST /users/login` → authenticates user, returns `{ token, user, expiresIn }`.
3. Client sends `Authorization` header with requests that require authentication.
4. Server validates token on protected routes via `authMiddleware`.

---

## Endpoints — Summary & Examples

> All request/response shapes and full schemas are defined in the OpenAPI file. Example requests/responses below are illustrative.

### Health
- **GET /health**
  - **Purpose:** Basic health check.
  - **Response:** `200 { status: "ok", timestamp, uptime }`

### Users / Auth
- **POST /users/register**
  - **Body:** `{ "email": "user@example.com", "password": "secret", "displayName": "Alice" }`
  - **Response:** `201 { token, user, expiresIn }`

- **POST /users/login**
  - **Body:** `{ "email": "user@example.com", "password": "secret" }`
  - **Response:** `200 { token, user, expiresIn }`

- **GET /users/{id}**
  - **Auth required**
  - **Response:** `200 { id, email, displayName, score, createdAt }`

- **POST /users/{id}/device-token**
  - **Auth required**
  - **Purpose:** Register push notification token for the user.
  - **Body:** `{ token: "<device-token>", platform: "web" | "android" }`
  - **Response:** `201 { id, userId, token, platform, createdAt }`

### Events
- **GET /events**
  - **Query:** `?lat=..&lon=..&startDate=YYYY-MM-DD&endDate=YYYY-MM-DD`
  - **Purpose:** List astronomical events (filtered by date and/or location).
  - **Response:** `200 { events: [ Event ] }`

- **GET /events/{id}**
  - **Purpose:** Event details including visibilityEstimate.
  - **Response:** `200 { event }`

### Dark Sites
- **GET /darksites/nearest**
  - **Query (required):** `?lat=..&lon=..&limit=10`
  - **Purpose:** Returns nearest dark-site locations sorted by distance and including `distance` field.
  - **Response:** `200 { items: [ DarkSite ] }`

### Visits & Gamification
- **POST /visits**
  - **Auth required**
  - **Body:** `{ eventId?: string, darkSiteId?: string, lat?: number, lon?: number, photoUrl?: string }`
  - **Purpose:** Report a visit; computes visibility, awards points, may grant badges.
  - **Response:** `201 { visit, pointsAwarded, newlyEarnedBadges }`

- **GET /users/{id}/badges**
  - **Purpose:** Retrieve badges earned by a user.
  - **Response:** `200 { items: [ Badge ] }`

- **GET /leaderboard**
  - **Query:** `?limit=100`
  - **Purpose:** Global leaderboard of top users by score.
  - **Response:** `200 { items: [ { rank, user, score } ] }`

### Notifications
- **POST /notifications/device-token**
  - **Auth required**
  - **Body:** `{ token: "<device-token>", platform: "web" | "android" }`
  - **Purpose:** Register/update device token for push notifications.
  - **Response:** `201 { deviceToken }`

---

## Error Handling
- Standard HTTP response codes:
  - `200` — OK
  - `201` — Created
  - `400` — Bad Request (validation)
  - `401` — Unauthorized (auth failure)
  - `403` — Forbidden (insufficient permissions)
  - `404` — Not Found
  - `409` — Conflict (e.g., duplicate email)
  - `500` — Internal Server Error
- Error responses follow a structure like: `{ error: "message" }`.

---

## Rate Limiting (Planned)
- **Planned policy:** Per-IP and per-user rate limits for public and authenticated endpoints.
  - Example proposal:
    - Unauthenticated endpoints: 100 requests / 10 minutes / IP
    - Authenticated endpoints: 300 requests / 10 minutes / user
  - Implementation: NGINX or API gateway + Redis for counters
- OpenAPI will be extended with `x-rate-limit` metadata when implemented.

---

## Versioning Strategy
- API will follow **URI-based versioning** for breaking changes: e.g., `/v1/events`, `/v2/events`.
- Initial development uses unversioned endpoints; upon public release, the OpenAPI spec will be published under `/v1`.
- Minor, backward-compatible changes (e.g., new optional fields) will not require a new version.
- New major versions will be documented in `CHANGELOG.md` and OpenAPI spec updated accordingly.

---

## Breaking Change Policy
- A change is considered **breaking** when it:
  - Removes or renames an existing required field.
  - Changes behavior of an existing endpoint contract in a non-backwards-compatible way.
  - Changes authentication/authorization semantics.

**Process for breaking changes:**
1. Describe the change in a PR with "BREAKING CHANGE" in the title and full justification.
2. Update `openapi.yaml` and include migration notes & examples.
3. Publish changes under a new major version (e.g., `/v2/...`) and keep `/v1` live for at least 90 days.
4. Notify integrators via release notes, repository issue, and (if available) subscriber email.

---

## Client Generation & Contract Tests
- An OpenAPI client generator (e.g., OpenAPI Generator) is used to produce strongly typed clients in the `apps/web` workspace.
- CI includes an API contract check workflow to ensure generated clients are in sync with the spec.

---

## Contact & Support
- API contract updates and discussions via repository PRs and issues.
- For urgent changes, open an issue labeled `api-contract` and tag maintainers.

---
