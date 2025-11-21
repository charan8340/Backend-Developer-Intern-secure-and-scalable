# Backend Intern Task — README

**Project:** Secure & Scalable Backend (Auth + RBAC + Products)

**Preview image (optional):** `file:///mnt/data/b5f961ff-3dd3-4ca3-9ba2-956e9467c765.png`

---

## 1. Goal

Build a secure, scalable backend with JWT authentication, role-based access control (RBAC), and a minimal products CRUD. Provide a small frontend to exercise the APIs.

This README documents the database design, RBAC model, JWT handling, API surface, and notes on security & scalability.

---

## 2. High-level architecture

* **FastAPI** (ASGI) backend exposing REST endpoints under `/v1/*`.
* **MySQL** (SQLAlchemy ORM) for persistent storage.
* Simple static frontend served from `/static` for manual testing.
* JWT access tokens + server-side refresh tokens for session management.

Diagram (simplified):

```
Client (browser)  <--HTTPS-->  FastAPI (uvicorn)
     |                              |
     |-- auth/login/register -----> |  (creates user, issues JWT + refresh)
     |<-- access_token -------------|
     |-- Authorization: Bearer ... ->|  (protected endpoints)

FastAPI <-> MySQL (users, roles, permissions, products, refresh_tokens)
```

---

## 3. Database schema & relationships

All tables were defined using SQLAlchemy models. The core tables to support RBAC and products are:

### Tables (summary)

1. `users` — stores account info

   * `id` (CHAR(36), PK), `username`, `email`, `password_hash`, `is_active`, `created_at`

2. `roles` — named roles (e.g., `user`, `admin`)

   * `id` (BIGINT, PK), `name`, `created_at`

3. `permissions` — granular permission names (e.g., `products.create`, `products.read`)

   * `id` (BIGINT, PK), `name`, `created_at`

4. `user_roles` — join table users ⇄ roles (many-to-many)

   * `user_id` (FK → users.id), `role_id` (FK → roles.id), `assigned_at`

5. `role_permissions` — join table roles ⇄ permissions (many-to-many)

   * `role_id` (FK → roles.id), `permission_id` (FK → permissions.id), `assigned_at`

6. `products` — product catalog

   * `id` (CHAR(36), PK), `title`, `description`, `price`, `stock`, `created_at`, `updated_at`

7. `refresh_tokens` — server-side refresh token storage

   * `id` (CHAR(36), PK), `user_id` (FK → users.id), `token_hash`, `issued_at`, `expires_at`, `revoked`

### Relationships & rationale

* **Users ↔ Roles:** many-to-many via `user_roles` so a user can have multiple roles (future flexibility).
* **Roles ↔ Permissions:** many-to-many via `role_permissions` so each role aggregates many permissions.
* **Permissions:** decoupled from roles so permissions can be fine-grained and reused.
* **Refresh tokens stored hashed** in `refresh_tokens` to avoid storing raw tokens in DB.

This structure is common and used in production systems because it separates *who* (roles) from *what* (permissions), allowing easy updates and audits.

---

## 4. Example sample data

* `roles`:

  * `1`: `user`
  * `2`: `admin`

* `permissions` (examples):

  * `1`: `products.read`
  * `2`: `products.create`
  * `3`: `products.update`
  * `4`: `products.delete`

* Assignments:

  * `role_permissions`: role `user` → `products.read`
  * `role_permissions`: role `admin` → `products.read, products.create, products.update, products.delete`

* `user_roles`: link users to either `user` or `admin` (or both)

---

## 5. Auth flow (Registration & Login)

### Registration

1. Client POSTs `/v1/auth/register` with `{ username, email, password, role }`.
2. Server validates input, hashes password (using passlib pbkdf2 or bcrypt), creates `users` record.
3. Server assigns the default role (`user`) or the requested role if allowed (for demo it's allowed). This writes `user_roles`.
4. Client receives basic confirmation — no tokens on register.

### Login

1. Client POSTs `/v1/auth/login` with `{ email, password }`.
2. Server verifies password using `verify_password`.
3. Server queries `list_user_roles(user_id)` to collect roles and optionally `get_permissions_for_user(user_id)`.
4. Server issues **access token (JWT)** with payload like:

```json
{ "sub": "<user-id>", "roles": ["admin"], "iat": 12345, "exp": 12399 }
```

5. Server also creates a **refresh token**, stores only the hashed token in DB (`refresh_tokens.token_hash`) and returns the raw refresh token to client (demo uses body; production should use HttpOnly cookie).

---

## 6. JWT: how it works here

* **Access token (JWT)**: short-lived (e.g., 30 minutes). Contains minimal claims: `sub` (user id) and `roles` (array). Signed with `settings.JWT_SECRET` using algorithm `HS256`.

* **Why roles in JWT?** Including roles in the token speeds up authorization checks without an extra DB call on every request. However, for authoritative permission checks you may still query DB for current role/permission state (trade-off discussed below).

* **Refresh tokens**: long-lived (e.g., 30 days). When access token expires client calls `/v1/auth/refresh` with refresh token; server verifies the hashed token exists and is not revoked/expired and issues a new access token (and can rotate refresh token).

**Security notes:**

* Store refresh tokens server-side hashed (SHA256) to avoid storing raw tokens.
* On logout, mark `revoked = true` for corresponding refresh token.
* For web UI, store access token in memory or in sessionStorage and store refresh token in an HttpOnly secure cookie in production.

---

## 7. Authorization & RBAC checks (server-side)

### `get_current_user` dependency

* Decodes and validates JWT (`decode_access_token`) — verifies signature and expiry.
* Extracts `sub` (user id) and fetches `users` record to ensure active status.
* Optionally attaches `roles` from `list_user_roles(db, user_id)` and `permissions` from `get_permissions_for_user(db, user_id)`.
* Returns a compact `user` dict `{id, username, roles, permissions}` for downstream endpoints.

### `require_admin` (example)

* A small dependency that simply checks `"admin" in user['roles']` and raises 403 if missing.

**Design choice:**

* We keep a *hybrid* approach: the JWT contains `roles` for fast checks while the server still reads authoritative permission sets when necessary (e.g., admin assignment, permission revocation).

---

## 8. Example API endpoints

* `POST /v1/auth/register` — register new user

* `POST /v1/auth/login` — login → returns `{ access_token, refresh_token }`

* `POST /v1/auth/refresh` — refresh access token using refresh_token

* `POST /v1/auth/logout` — revoke refresh token

* `GET /v1/products` — public list (or protected if you prefer)

* `GET /v1/products/{id}` — product detail

* `POST /v1/products` — **admin-only** create product

* `PATCH /v1/products/{id}` / `PUT` — **admin-only** update product

* `DELETE /v1/products/{id}` — **admin-only** delete product

* `POST /v1/admin/assign-role` — admin only endpoint to assign roles to users

---

## 9. Security best-practices applied

* **Password hashing** with a secure algorithm (PBKDF2 / bcrypt via passlib). Do not store raw passwords.
* **JWT signature** with strong secret and reasonable expiration.
* **Refresh tokens** stored hashed and revocable.
* **Input validation & pydantic** models for request bodies and responses to avoid malformed data.
* **CORS** configured to allow only expected origins during dev.
* **Least privilege:** server enforces RBAC; client enforces UI-level gating but server remains authoritative.

---

## 10. Scalability notes (short)

* **Stateless APIs:** access tokens are stateless—easy to scale horizontally behind a load balancer.
* **Refresh tokens & revocation:** refresh tokens are stored server-side, so revocation requires DB lookup. To avoid DB hits under heavy load, keep refresh checks infrequent or use an in-memory cache (Redis) to store recently revoked token ids.
* **Caching:** product list can be cached in Redis and invalidated on changes.
* **Microservices:** authentication service can be separated from product service; central auth issues tokens used by other services.
* **Connection pooling:** SQLAlchemy engine configured with pool options and `pool_pre_ping=True`.

---

## 11. How to run (dev)

1. Create virtual env & install deps from `requirements.txt`.
2. Create `.env` with `DATABASE_URL`, `JWT_SECRET` etc.
3. Ensure MySQL is running and reachable by `DATABASE_URL`.
4. Start app from project root:

```bash
uvicorn app.main:app --reload
```

5. Visit `http://127.0.0.1:8000/static/index.html` to use the simple UI.

---

## 12. Where to add changes / next steps

* Add more fine-grained permissions like `products.bulk_import` or `products.publish` as needed.
* Add audit tables for role/permission changes to track who changed what and when.
* Improve refresh flow by rotating refresh tokens and storing short identifier in cookie.
* Add tests for auth and RBAC paths (unit + integration).
